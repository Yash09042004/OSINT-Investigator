# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         risk_scorer
# Purpose:      Multi-factor entity risk scoring engine for PRISM OSINT platform.
#               Scores entities on a 0-100 scale using 5 weighted dimensions:
#                 1. Threat Indicators  (30%)
#                 2. Graph Centrality   (20%)
#                 3. Vulnerability      (20%)
#                 4. Infrastructure     (15%)
#                 5. Data Exposure      (15%)
#
# Authors:      Yash Patil, Soumitra Bapat, Sharvari Jadhav
# Copyright:    (c) PRISM Team 2026
# Licence:      MIT
# -------------------------------------------------------------------------------

import json
import logging
import time
import math
from collections import defaultdict

try:
    import networkx as nx
except ImportError:
    nx = None

log = logging.getLogger(f"spiderfoot.{__name__}")

# ── Risk level thresholds ──────────────────────────────────────────────
RISK_LEVELS = {
    'CRITICAL': 80,
    'HIGH':     60,
    'MEDIUM':   40,
    'LOW':      20,
    'INFO':      0,
}

# ── Dimension weights (must sum to 1.0) ────────────────────────────────
DIMENSION_WEIGHTS = {
    'threat':     0.30,
    'graph':      0.20,
    'vuln':       0.20,
    'infra':      0.15,
    'exposure':   0.15,
}

# ── Event type → dimension signal maps ─────────────────────────────────

# Events that indicate known-malicious or blacklisted association
THREAT_EVENT_TYPES = {
    # High-severity threat indicators  (weight 1.0)
    'MALICIOUS_IPADDR':                          1.0,
    'MALICIOUS_INTERNET_NAME':                   1.0,
    'MALICIOUS_EMAILADDR':                       1.0,
    'MALICIOUS_COHOST':                          0.8,
    'MALICIOUS_AFFILIATE_INTERNET_NAME':         0.8,
    'MALICIOUS_AFFILIATE_IPADDR':                0.8,
    'MALICIOUS_NETBLOCK':                        0.7,
    'MALICIOUS_SUBNET':                          0.7,
    'MALICIOUS_ASN':                             0.6,
    'MALICIOUS_BITCOIN_ADDRESS':                 1.0,
    'MALICIOUS_PHONE_NUMBER':                    0.8,
    # Blacklisted indicators
    'BLACKLISTED_IPADDR':                        0.9,
    'BLACKLISTED_INTERNET_NAME':                 0.9,
    'BLACKLISTED_AFFILIATE_INTERNET_NAME':       0.7,
    'BLACKLISTED_AFFILIATE_IPADDR':              0.7,
    'BLACKLISTED_COHOST':                        0.6,
    'BLACKLISTED_SUBNET':                        0.5,
    'BLACKLISTED_NETBLOCK':                      0.5,
    # Defaced indicators
    'DEFACED_INTERNET_NAME':                     0.8,
    'DEFACED_IPADDR':                            0.8,
    'DEFACED_AFFILIATE_INTERNET_NAME':           0.6,
    'DEFACED_AFFILIATE_IPADDR':                  0.6,
    'DEFACED_COHOST':                            0.5,
    # TOR exit / proxy
    'TOR_EXIT_NODE':                             0.4,
    'PROXY_HOST':                                0.3,
    'VPN_HOST':                                  0.2,
}

VULN_EVENT_TYPES = {
    'VULNERABILITY_CVE_CRITICAL':      1.0,
    'VULNERABILITY_CVE_HIGH':          0.8,
    'VULNERABILITY_CVE_MEDIUM':        0.5,
    'VULNERABILITY_CVE_LOW':           0.2,
    'VULNERABILITY_GENERAL':           0.4,
    'VULNERABILITY_DISCLOSURE':        0.3,
}

INFRA_EVENT_TYPES = {
    'TCP_PORT_OPEN':                   0.15,
    'UDP_PORT_OPEN':                   0.10,
    'SSL_CERTIFICATE_EXPIRED':         0.7,
    'SSL_CERTIFICATE_EXPIRING':        0.3,
    'SSL_CERTIFICATE_MISMATCH':        0.6,
    'CO_HOSTED_SITE':                  0.1,
    'INTERNET_NAME_UNRESOLVED':        0.2,
}

EXPOSURE_EVENT_TYPES = {
    'EMAILADDR_COMPROMISED':           0.9,
    'ACCOUNT_EXTERNAL_OWNED_COMPROMISED': 0.9,
    'ACCOUNT_EXTERNAL_USER_SHARED_COMPROMISED': 0.8,
    'PASSWORD_COMPROMISED':            1.0,
    'HASH_COMPROMISED':                0.8,
    'PHONE_NUMBER_COMPROMISED':        0.7,
    'DARKNET_MENTION_URL':             0.8,
    'DARKNET_MENTION_CONTENT':         0.7,
    'LEAKSITE_URL':                    0.9,
    'LEAKSITE_CONTENT':                0.8,
    'INTERESTING_FILE':                0.2,
    'CREDIT_CARD_NUMBER':              0.6,
    'IBAN_NUMBER':                     0.4,
}

# Entity types we score (non-data, non-internal)
SCOREABLE_ENTITY_TYPES = {
    'IP_ADDRESS', 'IPV6_ADDRESS', 'INTERNET_NAME', 'DOMAIN_NAME',
    'EMAILADDR', 'EMAILADDR_GENERIC', 'HUMAN_NAME', 'PHONE_NUMBER',
    'USERNAME', 'BITCOIN_ADDRESS', 'ETHEREUM_ADDRESS', 'COMPANY_NAME',
    'SOCIAL_MEDIA', 'DOMAIN_NAME_PARENT', 'AFFILIATE_INTERNET_NAME',
    'AFFILIATE_IPADDR', 'AFFILIATE_DOMAIN_NAME', 'AFFILIATE_EMAILADDR',
}


# ═══════════════════════════════════════════════════════════════════════
class EntityRiskScorer:
    """Multi-factor risk scoring engine for OSINT entities.

    Computes a normalised 0-100 risk score for every scoreable entity
    discovered during a scan, decomposed across five weighted dimensions.

    Usage::

        scorer = EntityRiskScorer(dbh)
        results = scorer.score_all_entities(scan_id)
        summary = scorer.get_scan_risk_summary(results)
    """

    def __init__(self, dbh):
        """Initialise with a SpiderFootDb handle.

        Args:
            dbh: An open SpiderFootDb instance.
        """
        self.dbh = dbh
        self.log = logging.getLogger(f"spiderfoot.{__name__}")

    # ── public API ─────────────────────────────────────────────────────

    def score_all_entities(self, scan_id):
        """Score every scoreable entity in the given scan.

        Builds an event index keyed by (entity_hash, entity_data), computes
        the five dimension sub-scores, and returns a sorted list of scored
        entity dicts (highest risk first).

        Args:
            scan_id (str): Scan instance GUID.

        Returns:
            list[dict]: Each dict contains:
                entity_hash, entity_type, entity_data,
                risk_score, risk_level,
                threat_score, graph_score, vuln_score, infra_score, exposure_score,
                details (dict with per-dimension breakdown)
        """
        self.log.info(f"[RiskScorer] Starting risk scoring for scan {scan_id}")
        t0 = time.time()

        # ── 1. Fetch all scan results ──────────────────────────────────
        events = self._fetch_events(scan_id)
        if not events:
            self.log.warning("[RiskScorer] No events found for scan")
            return []

        # ── 2. Build entity index ──────────────────────────────────────
        entity_map, child_events = self._build_entity_index(events)

        # ── 3. Build graph and compute centrality (if networkx available)
        centrality = self._compute_centrality(events)

        # ── 4. Score each entity ───────────────────────────────────────
        scored = []
        for key, entity_info in entity_map.items():
            e_hash = entity_info['hash']
            e_type = entity_info['type']
            e_data = entity_info['data']

            # Gather child event types for this entity
            children = child_events.get(e_hash, [])

            # Compute per-dimension scores
            threat = self._calc_threat_score(e_type, children)
            graph  = self._calc_graph_score(e_hash, centrality)
            vuln   = self._calc_vuln_score(children)
            infra  = self._calc_infra_score(children)
            exposure = self._calc_exposure_score(children)

            # Weighted final score
            risk_score = (
                threat   * DIMENSION_WEIGHTS['threat']   +
                graph    * DIMENSION_WEIGHTS['graph']     +
                vuln     * DIMENSION_WEIGHTS['vuln']      +
                infra    * DIMENSION_WEIGHTS['infra']     +
                exposure * DIMENSION_WEIGHTS['exposure']
            )
            risk_score = round(min(100.0, max(0.0, risk_score)), 2)

            risk_level = self._classify_risk(risk_score)

            details = {
                'threat_signals':   self._list_signals(children, THREAT_EVENT_TYPES),
                'vuln_signals':     self._list_signals(children, VULN_EVENT_TYPES),
                'infra_signals':    self._list_signals(children, INFRA_EVENT_TYPES),
                'exposure_signals': self._list_signals(children, EXPOSURE_EVENT_TYPES),
                'child_event_count': len(children),
            }

            scored.append({
                'entity_hash':   e_hash,
                'entity_type':   e_type,
                'entity_data':   e_data,
                'risk_score':    risk_score,
                'risk_level':    risk_level,
                'threat_score':  round(threat, 2),
                'graph_score':   round(graph, 2),
                'vuln_score':    round(vuln, 2),
                'infra_score':   round(infra, 2),
                'exposure_score': round(exposure, 2),
                'details':       details,
            })

        # Sort descending by risk_score
        scored.sort(key=lambda x: x['risk_score'], reverse=True)

        elapsed = round(time.time() - t0, 3)
        self.log.info(
            f"[RiskScorer] Scored {len(scored)} entities in {elapsed}s  "
            f"(highest={scored[0]['risk_score'] if scored else 0})"
        )
        return scored

    def get_scan_risk_summary(self, scored_entities):
        """Aggregate scan-level risk statistics from scored entity list.

        Args:
            scored_entities (list[dict]): Output of ``score_all_entities``.

        Returns:
            dict with:
                total_entities, overall_risk_score, overall_risk_level,
                risk_distribution (count per level), dimension_averages,
                top_5_entities
        """
        if not scored_entities:
            return {
                'total_entities': 0,
                'overall_risk_score': 0.0,
                'overall_risk_level': 'INFO',
                'risk_distribution': {k: 0 for k in RISK_LEVELS},
                'dimension_averages': {k: 0.0 for k in DIMENSION_WEIGHTS},
                'top_5_entities': [],
            }

        n = len(scored_entities)

        # Overall = mean risk
        overall = round(sum(e['risk_score'] for e in scored_entities) / n, 2)

        # Distribution
        dist = defaultdict(int)
        for e in scored_entities:
            dist[e['risk_level']] += 1
        distribution = {k: dist.get(k, 0) for k in RISK_LEVELS}

        # Dimension averages
        dim_avg = {
            'threat':   round(sum(e['threat_score']   for e in scored_entities) / n, 2),
            'graph':    round(sum(e['graph_score']     for e in scored_entities) / n, 2),
            'vuln':     round(sum(e['vuln_score']      for e in scored_entities) / n, 2),
            'infra':    round(sum(e['infra_score']     for e in scored_entities) / n, 2),
            'exposure': round(sum(e['exposure_score']  for e in scored_entities) / n, 2),
        }

        top5 = scored_entities[:5]

        return {
            'total_entities':     n,
            'overall_risk_score': overall,
            'overall_risk_level': self._classify_risk(overall),
            'risk_distribution':  distribution,
            'dimension_averages': dim_avg,
            'top_5_entities':     top5,
        }

    def store_risk_scores(self, scan_id, scored_entities):
        """Persist scored entities to the database.

        Args:
            scan_id (str): Scan instance GUID.
            scored_entities (list[dict]): Output of ``score_all_entities``.

        Returns:
            bool: True on success.
        """
        if not scored_entities:
            return True

        qry = """
            INSERT INTO tbl_scan_risk_scores
            (scan_instance_id, entity_hash, entity_type, entity_data,
             risk_score, risk_level,
             threat_score, graph_score, vuln_score, infra_score, exposure_score,
             details, created_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """

        rows = []
        for e in scored_entities:
            rows.append((
                scan_id,
                e['entity_hash'],
                e['entity_type'],
                e['entity_data'],
                e['risk_score'],
                e['risk_level'],
                e['threat_score'],
                e['graph_score'],
                e['vuln_score'],
                e['infra_score'],
                e['exposure_score'],
                json.dumps(e['details']),
            ))

        try:
            with self.dbh.dbhLock:
                self.dbh.dbh.executemany(qry, rows)
                self.dbh.conn.commit()
            self.log.info(f"[RiskScorer] Stored {len(rows)} risk scores for scan {scan_id}")
            return True
        except Exception as e:
            self.log.error(f"[RiskScorer] Failed to store risk scores: {e}")
            return False

    # ── dimension calculators ──────────────────────────────────────────

    def _calc_threat_score(self, entity_type, child_events):
        """Score based on threat / blacklist / malicious indicators.

        Strategy:
         - The entity itself being a threat type gives 60 base points.
         - Each matching child event adds up to 40 more points (diminishing).
        """
        score = 0.0

        # Entity-level: if the entity type itself is a threat indicator
        if entity_type in THREAT_EVENT_TYPES:
            score += 60.0 * THREAT_EVENT_TYPES[entity_type]

        # Child-level: sum of weighted threat children (cap contribution at 40)
        child_sum = 0.0
        for ev_type, _ in child_events:
            if ev_type in THREAT_EVENT_TYPES:
                child_sum += THREAT_EVENT_TYPES[ev_type]

        # Apply diminishing returns via log-scaling
        if child_sum > 0:
            score += min(40.0, 20.0 * math.log2(1 + child_sum))

        return min(100.0, score)

    def _calc_graph_score(self, entity_hash, centrality):
        """Score based on graph topology (PageRank + betweenness).

        Higher centrality ⇒ more structurally important in the threat graph
        ⇒ higher risk score.  We normalise centrality values to 0-100.
        """
        if not centrality:
            return 0.0

        pr = centrality.get('pagerank', {}).get(entity_hash, 0.0)
        bt = centrality.get('betweenness', {}).get(entity_hash, 0.0)

        # Normalise against max values in the graph
        pr_max = centrality.get('pagerank_max', 1e-9)
        bt_max = centrality.get('betweenness_max', 1e-9)

        pr_norm = (pr / pr_max) * 100.0 if pr_max > 0 else 0.0
        bt_norm = (bt / bt_max) * 100.0 if bt_max > 0 else 0.0

        # Weighted blend: 60 % pagerank, 40 % betweenness
        return min(100.0, pr_norm * 0.6 + bt_norm * 0.4)

    def _calc_vuln_score(self, child_events):
        """Score based on vulnerability indicators (CVEs, disclosures)."""
        score = 0.0
        for ev_type, _ in child_events:
            if ev_type in VULN_EVENT_TYPES:
                score += VULN_EVENT_TYPES[ev_type] * 30.0
        return min(100.0, score)

    def _calc_infra_score(self, child_events):
        """Score based on infrastructure risk indicators."""
        score = 0.0
        for ev_type, _ in child_events:
            if ev_type in INFRA_EVENT_TYPES:
                score += INFRA_EVENT_TYPES[ev_type] * 25.0
        return min(100.0, score)

    def _calc_exposure_score(self, child_events):
        """Score based on data exposure / credential leaks."""
        score = 0.0
        for ev_type, _ in child_events:
            if ev_type in EXPOSURE_EVENT_TYPES:
                score += EXPOSURE_EVENT_TYPES[ev_type] * 30.0
        return min(100.0, score)

    # ── helper methods ─────────────────────────────────────────────────

    def _fetch_events(self, scan_id):
        """Fetch all results for a scan from the database.

        Returns:
            list of tuples: (hash, type, data, source_event_hash, module, confidence)
        """
        qry = """
            SELECT hash, type, data, source_event_hash, module, confidence
            FROM tbl_scan_results
            WHERE scan_instance_id = ?
        """
        try:
            with self.dbh.dbhLock:
                self.dbh.dbh.execute(qry, (scan_id,))
                return self.dbh.dbh.fetchall()
        except Exception as e:
            self.log.error(f"[RiskScorer] DB fetch failed: {e}")
            return []

    def _build_entity_index(self, events):
        """Partition events into scoreable entities and their child events.

        Returns:
            entity_map: {entity_hash: {hash, type, data}}
            child_events: {entity_hash: [(child_type, child_data), ...]}
        """
        entity_map = {}
        child_events = defaultdict(list)

        for row in events:
            r_hash, r_type, r_data, r_src_hash, r_module, r_conf = row

            # Determine if this event is a scoreable entity
            if r_type in SCOREABLE_ENTITY_TYPES:
                if r_hash not in entity_map:
                    entity_map[r_hash] = {
                        'hash': r_hash,
                        'type': r_type,
                        'data': r_data or '',
                    }

            # All events are potential children of their source entity
            if r_src_hash and r_src_hash != 'ROOT':
                child_events[r_src_hash].append((r_type, r_data))

        return entity_map, child_events

    def _compute_centrality(self, events):
        """Build a lightweight graph and compute centrality measures.

        Returns:
            dict with 'pagerank', 'betweenness', and their max values,
            or empty dict if networkx is unavailable.
        """
        if nx is None:
            return {}

        G = nx.DiGraph()
        for row in events:
            r_hash, r_type, r_data, r_src_hash, r_module, r_conf = row
            G.add_node(r_hash, type=r_type)
            if r_src_hash and r_src_hash != 'ROOT':
                G.add_edge(r_src_hash, r_hash)

        if G.number_of_nodes() < 2:
            return {}

        try:
            pr = nx.pagerank(G, alpha=0.85, max_iter=100, tol=1e-06)
        except Exception:
            pr = {n: 1.0 / G.number_of_nodes() for n in G.nodes()}

        try:
            bt = nx.betweenness_centrality(G, normalized=True)
        except Exception:
            bt = {n: 0.0 for n in G.nodes()}

        pr_max = max(pr.values()) if pr else 1e-9
        bt_max = max(bt.values()) if bt else 1e-9

        return {
            'pagerank':       pr,
            'betweenness':    bt,
            'pagerank_max':   pr_max,
            'betweenness_max': bt_max,
        }

    @staticmethod
    def _classify_risk(score):
        """Map a 0-100 score to a risk level string."""
        for level, threshold in RISK_LEVELS.items():
            if score >= threshold:
                return level
        return 'INFO'

    @staticmethod
    def _list_signals(child_events, signal_map):
        """Return list of (event_type, weight) for matching children."""
        found = []
        seen = set()
        for ev_type, _ in child_events:
            if ev_type in signal_map and ev_type not in seen:
                found.append({'type': ev_type, 'weight': signal_map[ev_type]})
                seen.add(ev_type)
        return found
