# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         graph_algorithms
# Purpose:      Graph analysis algorithms for PRISM OSINT platform.
#               Provides community detection, centrality calculation,
#               and anomaly detection on OSINT intelligence graphs.
#
# Authors:      Yash Patil, Soumitra Bapat, Sharvari Jadhav
# Copyright:    (c) PRISM Team 2026
# Licence:      MIT
# -------------------------------------------------------------------------------

import logging
import json
from collections import defaultdict

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

try:
    import community as community_louvain
    HAS_LOUVAIN = True
except ImportError:
    HAS_LOUVAIN = False

log = logging.getLogger(f"spiderfoot.graph_algorithms")


class GraphAnalyzer:
    """Runs graph-theoretic analysis algorithms on an OSINT intelligence graph.

    Supports:
      - Community detection (Louvain, fallback: connected components)
      - Centrality calculation (PageRank + betweenness)
      - Anomaly detection (high-degree, bridge nodes, isolated nodes)
      - Aggregated correlation pipeline (``run_all_correlations``)

    Args:
        graph: A ``networkx.Graph`` or ``networkx.DiGraph`` built by
               ``SpiderFootGraphEngine``.
    """

    def __init__(self, graph):
        self.graph = graph
        self.log = logging.getLogger(f"spiderfoot.graph_algorithms")

    # ── Community Detection ────────────────────────────────────────────

    def detect_communities(self):
        """Detect entity communities using the Louvain algorithm.

        Falls back to connected-components-based grouping when  
        ``python-louvain`` is unavailable.

        Returns:
            list[dict]: Each dict describes one community::

                {
                    "community_id": int,
                    "size": int,
                    "nodes": [node_id, ...],
                    "risk_level": str   # HIGH / MEDIUM / LOW
                }
        """
        if self.graph.number_of_nodes() == 0:
            return []

        # Work on an undirected copy for community detection
        G_undirected = self.graph.to_undirected() if HAS_NETWORKX else self.graph

        # ── Louvain ────────────────────────────────────────────────────
        if HAS_LOUVAIN and HAS_NETWORKX:
            try:
                partition = community_louvain.best_partition(G_undirected)
                community_map = defaultdict(list)
                for node, cid in partition.items():
                    community_map[cid].append(node)

                communities = []
                for cid, nodes in community_map.items():
                    size = len(nodes)
                    risk = "HIGH" if size > 20 else ("MEDIUM" if size > 5 else "LOW")
                    communities.append({
                        "community_id": cid,
                        "size": size,
                        "nodes": nodes[:50],   # cap payload
                        "risk_level": risk,
                    })
                communities.sort(key=lambda c: c["size"], reverse=True)
                self.log.info(f"[GraphAnalyzer] Louvain: {len(communities)} communities")
                return communities
            except Exception as e:
                self.log.warning(f"[GraphAnalyzer] Louvain failed: {e}, falling back")

        # ── Fallback: connected components ─────────────────────────────
        if HAS_NETWORKX:
            try:
                components = list(nx.connected_components(G_undirected))
                communities = []
                for i, comp in enumerate(components):
                    nodes = list(comp)
                    size = len(nodes)
                    risk = "HIGH" if size > 20 else ("MEDIUM" if size > 5 else "LOW")
                    communities.append({
                        "community_id": i,
                        "size": size,
                        "nodes": nodes[:50],
                        "risk_level": risk,
                    })
                communities.sort(key=lambda c: c["size"], reverse=True)
                self.log.info(f"[GraphAnalyzer] Components: {len(communities)} communities")
                return communities
            except Exception as e:
                self.log.error(f"[GraphAnalyzer] Community detection failed: {e}")

        return []

    # ── Centrality ─────────────────────────────────────────────────────

    def calculate_centrality(self):
        """Calculate PageRank and betweenness centrality for all nodes.

        Returns:
            list[dict]: Top-100 nodes by PageRank, each with::

                {
                    "node": str,
                    "type": str,
                    "pagerank": float,
                    "betweenness": float,
                    "risk_level": str,
                    "label": str
                }
        """
        if not HAS_NETWORKX or self.graph.number_of_nodes() < 2:
            return []

        try:
            pr = nx.pagerank(self.graph, alpha=0.85, max_iter=100, tol=1e-06)
        except Exception as e:
            self.log.warning(f"[GraphAnalyzer] PageRank failed: {e}")
            pr = {n: 1.0 / max(self.graph.number_of_nodes(), 1) for n in self.graph.nodes()}

        try:
            bt = nx.betweenness_centrality(self.graph, normalized=True)
        except Exception as e:
            self.log.warning(f"[GraphAnalyzer] Betweenness failed: {e}")
            bt = {n: 0.0 for n in self.graph.nodes()}

        pr_max = max(pr.values()) if pr else 1
        results = []
        for node, score in pr.items():
            pr_norm = score / pr_max if pr_max > 0 else 0
            risk = "HIGH" if pr_norm > 0.7 else ("MEDIUM" if pr_norm > 0.3 else "LOW")
            attrs = self.graph.nodes.get(node, {})
            results.append({
                "node": node,
                "type": attrs.get("type", "UNKNOWN"),
                "pagerank": round(score, 6),
                "betweenness": round(bt.get(node, 0.0), 6),
                "risk_level": risk,
                "label": attrs.get("label", attrs.get("data", str(node)))[:60],
            })

        results.sort(key=lambda x: x["pagerank"], reverse=True)
        self.log.info(f"[GraphAnalyzer] Centrality: {len(results)} nodes")
        return results[:100]

    # ── Anomaly Detection ──────────────────────────────────────────────

    def detect_anomalies(self):
        """Detect structural anomalies in the graph.

        Identifies:
        - **High-degree nodes** — abnormally many connections
        - **Bridge nodes** — whose removal would disconnect the graph
        - **Isolated nodes** — no connections at all

        Returns:
            list[dict]: Each anomaly is::

                {
                    "node": str,
                    "type": str,
                    "anomaly_type": str,
                    "degree": int,
                    "risk_level": str,
                    "description": str
                }
        """
        if not HAS_NETWORKX or self.graph.number_of_nodes() == 0:
            return []

        anomalies = []
        G_undirected = self.graph.to_undirected()

        # Degree statistics
        degrees = dict(G_undirected.degree())
        if degrees:
            values = list(degrees.values())
            avg = sum(values) / len(values)
            threshold = avg + 2 * (sum((v - avg) ** 2 for v in values) / len(values)) ** 0.5
            threshold = max(threshold, avg * 3, 5)
        else:
            avg = 0
            threshold = 5

        seen = set()

        # High-degree nodes
        for node, deg in degrees.items():
            if deg > threshold and node not in seen:
                attrs = self.graph.nodes.get(node, {})
                anomalies.append({
                    "node": node,
                    "type": attrs.get("type", "UNKNOWN"),
                    "anomaly_type": "HIGH_DEGREE",
                    "degree": deg,
                    "risk_level": "HIGH" if deg > threshold * 2 else "MEDIUM",
                    "description": f"Node has {deg} connections (avg={avg:.1f}, threshold={threshold:.1f})",
                })
                seen.add(node)

        # Bridge nodes (articulation points)
        try:
            bridges = set(nx.articulation_points(G_undirected))
            for node in bridges:
                if node not in seen:
                    attrs = self.graph.nodes.get(node, {})
                    anomalies.append({
                        "node": node,
                        "type": attrs.get("type", "UNKNOWN"),
                        "anomaly_type": "BRIDGE_NODE",
                        "degree": degrees.get(node, 0),
                        "risk_level": "MEDIUM",
                        "description": "Articulation point — removal would disconnect the graph",
                    })
                    seen.add(node)
        except Exception:
            pass

        # Isolated nodes
        for node, deg in degrees.items():
            if deg == 0 and node not in seen:
                attrs = self.graph.nodes.get(node, {})
                anomalies.append({
                    "node": node,
                    "type": attrs.get("type", "UNKNOWN"),
                    "anomaly_type": "ISOLATED_NODE",
                    "degree": 0,
                    "risk_level": "LOW",
                    "description": "Node has no connections",
                })

        self.log.info(f"[GraphAnalyzer] Anomalies: {len(anomalies)} detected")
        return anomalies

    # ── Aggregated pipeline ────────────────────────────────────────────

    def run_all_correlations(self):
        """Run all analysis algorithms and return a combined result dict.

        Returns:
            dict with keys ``communities``, ``centrality``, ``anomalies``,
            and summary statistics.
        """
        communities = self.detect_communities()
        centrality  = self.calculate_centrality()
        anomalies   = self.detect_anomalies()

        return {
            "communities": communities,
            "centrality":  centrality,
            "anomalies":   anomalies,
            "summary": {
                "num_communities": len(communities),
                "num_high_centrality": sum(1 for c in centrality if c["risk_level"] == "HIGH"),
                "num_anomalies": len(anomalies),
                "high_risk_anomalies": sum(1 for a in anomalies if a["risk_level"] == "HIGH"),
            }
        }
