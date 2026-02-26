#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         test_risk_scorer
# Purpose:      Comprehensive tests for the PRISM Entity Risk Scoring Engine.
#
# Usage:
#     cd /home/yash/Desktop/MEGA_PROJECT/spiderfoot
#     python3 test_risk_scorer.py
#
# Tests:
#     1. Basic scoring with realistic mock scan data
#     2. Multi-factor dimension validation (each dimension independently)
#     3. Database integration (store → retrieve → delete round-trip)
#     4. Edge cases (empty scan, single entity, all-malicious)
#     5. Scan-level summary aggregation
# -------------------------------------------------------------------------------

import os
import sys
import time
import json
import sqlite3
import hashlib
import tempfile
import traceback

# Add parent to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spiderfoot.db import SpiderFootDb
from spiderfoot.risk_scorer import EntityRiskScorer, RISK_LEVELS, DIMENSION_WEIGHTS

# ── Colour helpers ──────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

passed = 0
failed = 0

def header(title):
    print(f"\n{BOLD}{CYAN}{'═' * 70}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 70}{RESET}")

def test_pass(name, detail=""):
    global passed
    passed += 1
    print(f"  {GREEN}✓ PASS{RESET}  {name}  {YELLOW}{detail}{RESET}")

def test_fail(name, detail=""):
    global failed
    failed += 1
    print(f"  {RED}✗ FAIL{RESET}  {name}  {RED}{detail}{RESET}")


# ── Helpers ─────────────────────────────────────────────────────────────
def make_hash(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def create_test_db():
    """Create a fresh temporary SQLite DB with full PRISM schema."""
    tmpfile = tempfile.mktemp(suffix='.db', prefix='prism_risk_test_')
    opts = {
        "__database": tmpfile,
        "__modules__": {},
    }
    dbh = SpiderFootDb(opts, init=True)
    return dbh, tmpfile

def create_scan(dbh, scan_id, name="Test Scan", target="example.com"):
    """Insert a scan instance into the database."""
    ts = int(time.time() * 1000)
    qry = """INSERT INTO tbl_scan_instance
             (guid, name, seed_target, created, started, ended, status)
             VALUES (?, ?, ?, ?, ?, 0, 'FINISHED')"""
    with dbh.dbhLock:
        dbh.dbh.execute(qry, (scan_id, name, target, ts, ts))
        dbh.conn.commit()

def insert_event(dbh, scan_id, event_hash, event_type, data, source_hash="ROOT",
                 module="test_module", confidence=100, risk=0):
    """Insert a scan result event."""
    ts = int(time.time() * 1000)
    qry = """INSERT INTO tbl_scan_results
             (scan_instance_id, hash, type, generated, confidence, visibility,
              risk, module, data, false_positive, source_event_hash)
             VALUES (?, ?, ?, ?, ?, 100, ?, ?, ?, 0, ?)"""
    with dbh.dbhLock:
        dbh.dbh.execute(qry, (scan_id, event_hash, event_type, ts,
                              confidence, risk, module, data, source_hash))
        dbh.conn.commit()


# ═══════════════════════════════════════════════════════════════════════
#  TEST 1: Basic scoring with realistic mock data
# ═══════════════════════════════════════════════════════════════════════
def test_basic_scoring():
    header("TEST 1: Basic Scoring with Realistic Mock Data")
    dbh, tmpfile = create_test_db()

    try:
        scan_id = "test-scan-001"
        create_scan(dbh, scan_id, "Basic Scoring Test", "example.com")

        # Create root event
        root_hash = make_hash("ROOT")
        insert_event(dbh, scan_id, root_hash, "ROOT", "example.com")

        # Entity: IP address
        ip_hash = make_hash("93.184.216.34")
        insert_event(dbh, scan_id, ip_hash, "IP_ADDRESS", "93.184.216.34",
                     source_hash=root_hash)

        # Entity: Domain
        dom_hash = make_hash("example.com")
        insert_event(dbh, scan_id, dom_hash, "INTERNET_NAME", "example.com",
                     source_hash=root_hash)

        # Entity: Email
        email_hash = make_hash("admin@example.com")
        insert_event(dbh, scan_id, email_hash, "EMAILADDR", "admin@example.com",
                     source_hash=root_hash)

        # Child events for the IP (malicious + open port)
        mal_hash = make_hash("malicious_ip_flag")
        insert_event(dbh, scan_id, mal_hash, "MALICIOUS_IPADDR",
                     "Listed on AbuseIPDB", source_hash=ip_hash, module="sfp_abuseipdb")

        port_hash = make_hash("port_80")
        insert_event(dbh, scan_id, port_hash, "TCP_PORT_OPEN",
                     "80/tcp", source_hash=ip_hash, module="sfp_portscan")

        # Child events for the email (compromised)
        comp_hash = make_hash("email_compromised")
        insert_event(dbh, scan_id, comp_hash, "EMAILADDR_COMPROMISED",
                     "Found in breach database", source_hash=email_hash, module="sfp_haveibeenpwned")

        # Run scoring
        scorer = EntityRiskScorer(dbh)
        results = scorer.score_all_entities(scan_id)

        # Validate
        if not results:
            test_fail("Scoring returned results", "Got empty list")
            return

        test_pass("Scoring returned results", f"{len(results)} entities scored")

        # All scores should be 0-100
        all_valid = all(0 <= e['risk_score'] <= 100 for e in results)
        if all_valid:
            test_pass("All scores in 0–100 range")
        else:
            test_fail("All scores in 0–100 range")

        # All entities should have a valid risk level
        valid_levels = set(RISK_LEVELS.keys())
        all_levels_valid = all(e['risk_level'] in valid_levels for e in results)
        if all_levels_valid:
            test_pass("All risk levels valid", f"Levels: {[e['risk_level'] for e in results]}")
        else:
            test_fail("All risk levels valid")

        # The IP with MALICIOUS flag should score higher than plain domain
        ip_score = next((e for e in results if e['entity_data'] == '93.184.216.34'), None)
        dom_score = next((e for e in results if e['entity_data'] == 'example.com'), None)

        if ip_score and dom_score:
            if ip_score['risk_score'] > dom_score['risk_score']:
                test_pass("Malicious IP scores higher than clean domain",
                          f"IP={ip_score['risk_score']} > Domain={dom_score['risk_score']}")
            else:
                test_fail("Malicious IP scores higher than clean domain",
                          f"IP={ip_score['risk_score']} <= Domain={dom_score['risk_score']}")
        else:
            test_fail("Found IP and domain entities in results")

        # Results should be sorted descending
        scores = [e['risk_score'] for e in results]
        if scores == sorted(scores, reverse=True):
            test_pass("Results sorted by risk score (descending)")
        else:
            test_fail("Results sorted by risk score (descending)")

        # Each entity should have all 5 dimension scores
        for e in results:
            for dim in ['threat_score', 'graph_score', 'vuln_score', 'infra_score', 'exposure_score']:
                if dim not in e:
                    test_fail(f"Entity has {dim} field")
                    return
        test_pass("All entities have 5 dimension scores")

        # Details should contain signal lists
        if ip_score and 'details' in ip_score:
            details = ip_score['details']
            if 'threat_signals' in details and len(details['threat_signals']) > 0:
                test_pass("IP entity has threat signals in details",
                          f"{len(details['threat_signals'])} signals found")
            else:
                test_fail("IP entity has threat signals in details")
        else:
            test_fail("IP entity has details field")

    except Exception as e:
        test_fail("Test execution", str(e))
        traceback.print_exc()
    finally:
        try:
            os.remove(tmpfile)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════
#  TEST 2: Multi-factor dimension validation
# ═══════════════════════════════════════════════════════════════════════
def test_dimension_scoring():
    header("TEST 2: Multi-Factor Dimension Validation")
    dbh, tmpfile = create_test_db()

    try:
        scan_id = "test-scan-002"
        create_scan(dbh, scan_id, "Dimension Test", "test.com")

        root_hash = make_hash("ROOT_DIM")
        insert_event(dbh, scan_id, root_hash, "ROOT", "test.com")

        # ── Entity A: High threat (malicious IP + blacklisted) ─────────
        a_hash = make_hash("entity_A_ip")
        insert_event(dbh, scan_id, a_hash, "IP_ADDRESS", "10.0.0.1",
                     source_hash=root_hash)
        insert_event(dbh, scan_id, make_hash("a_mal1"), "MALICIOUS_IPADDR",
                     "VT detection", source_hash=a_hash)
        insert_event(dbh, scan_id, make_hash("a_mal2"), "BLACKLISTED_IPADDR",
                     "Spamhaus", source_hash=a_hash)

        # ── Entity B: High vulnerability ───────────────────────────────
        b_hash = make_hash("entity_B_dom")
        insert_event(dbh, scan_id, b_hash, "INTERNET_NAME", "vuln-server.com",
                     source_hash=root_hash)
        insert_event(dbh, scan_id, make_hash("b_vuln1"), "VULNERABILITY_CVE_CRITICAL",
                     "CVE-2024-1234", source_hash=b_hash)
        insert_event(dbh, scan_id, make_hash("b_vuln2"), "VULNERABILITY_CVE_HIGH",
                     "CVE-2024-5678", source_hash=b_hash)

        # ── Entity C: High exposure ────────────────────────────────────
        c_hash = make_hash("entity_C_email")
        insert_event(dbh, scan_id, c_hash, "EMAILADDR", "leaked@test.com",
                     source_hash=root_hash)
        insert_event(dbh, scan_id, make_hash("c_comp"), "PASSWORD_COMPROMISED",
                     "plaintext password", source_hash=c_hash)
        insert_event(dbh, scan_id, make_hash("c_dark"), "DARKNET_MENTION_URL",
                     "http://dark.onion/leak", source_hash=c_hash)

        # ── Entity D: High infrastructure risk ─────────────────────────
        d_hash = make_hash("entity_D_server")
        insert_event(dbh, scan_id, d_hash, "IP_ADDRESS", "192.168.1.1",
                     source_hash=root_hash)
        insert_event(dbh, scan_id, make_hash("d_ssl"), "SSL_CERTIFICATE_EXPIRED",
                     "expired cert", source_hash=d_hash)
        insert_event(dbh, scan_id, make_hash("d_ssl2"), "SSL_CERTIFICATE_MISMATCH",
                     "mismatch", source_hash=d_hash)
        insert_event(dbh, scan_id, make_hash("d_port1"), "TCP_PORT_OPEN",
                     "22/tcp", source_hash=d_hash)
        insert_event(dbh, scan_id, make_hash("d_port2"), "TCP_PORT_OPEN",
                     "3389/tcp", source_hash=d_hash)

        # Run scoring
        scorer = EntityRiskScorer(dbh)
        results = scorer.score_all_entities(scan_id)

        entity_map = {e['entity_data']: e for e in results}

        # Entity A should have highest threat_score
        a = entity_map.get('10.0.0.1')
        b = entity_map.get('vuln-server.com')
        c = entity_map.get('leaked@test.com')
        d = entity_map.get('192.168.1.1')

        if a and a['threat_score'] > 0:
            test_pass("Entity A (malicious IP) has positive threat score",
                      f"threat={a['threat_score']}")
        else:
            test_fail("Entity A has positive threat score")

        if b and b['vuln_score'] > 0:
            test_pass("Entity B (vuln server) has positive vuln score",
                      f"vuln={b['vuln_score']}")
        else:
            test_fail("Entity B has positive vuln score")

        if c and c['exposure_score'] > 0:
            test_pass("Entity C (leaked email) has positive exposure score",
                      f"exposure={c['exposure_score']}")
        else:
            test_fail("Entity C has positive exposure score")

        if d and d['infra_score'] > 0:
            test_pass("Entity D (bad infra) has positive infra score",
                      f"infra={d['infra_score']}")
        else:
            test_fail("Entity D has positive infra score")

        # Entity A's threat should dominate its other dimensions
        if a and a['threat_score'] > a['vuln_score'] and a['threat_score'] > a['exposure_score']:
            test_pass("Entity A: threat dimension is the dominant factor")
        elif a:
            test_fail("Entity A: threat dimension is the dominant factor",
                      f"threat={a['threat_score']}, vuln={a['vuln_score']}, exposure={a['exposure_score']}")

        # Weights should sum to 1.0
        weight_sum = sum(DIMENSION_WEIGHTS.values())
        if abs(weight_sum - 1.0) < 0.001:
            test_pass("Dimension weights sum to 1.0", f"sum={weight_sum}")
        else:
            test_fail("Dimension weights sum to 1.0", f"sum={weight_sum}")

    except Exception as e:
        test_fail("Test execution", str(e))
        traceback.print_exc()
    finally:
        try:
            os.remove(tmpfile)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════
#  TEST 3: Database integration (store → retrieve → delete)
# ═══════════════════════════════════════════════════════════════════════
def test_database_integration():
    header("TEST 3: Database Integration (Store / Retrieve / Delete)")
    dbh, tmpfile = create_test_db()

    try:
        scan_id = "test-scan-003"
        create_scan(dbh, scan_id, "DB Integration Test", "db-test.com")

        root_hash = make_hash("ROOT_DB")
        insert_event(dbh, scan_id, root_hash, "ROOT", "db-test.com")

        # Create some entities
        for i in range(5):
            h = make_hash(f"entity_{i}")
            insert_event(dbh, scan_id, h, "IP_ADDRESS", f"10.0.0.{i}",
                         source_hash=root_hash)
            # Add a malicious child to odd-numbered entities
            if i % 2 == 1:
                mh = make_hash(f"mal_{i}")
                insert_event(dbh, scan_id, mh, "MALICIOUS_IPADDR",
                             f"Malicious flag for 10.0.0.{i}", source_hash=h)

        # Score
        scorer = EntityRiskScorer(dbh)
        results = scorer.score_all_entities(scan_id)

        if len(results) > 0:
            test_pass("Scoring produced results", f"{len(results)} entities")
        else:
            test_fail("Scoring produced results")
            return

        # Store via scorer's method
        store_ok = scorer.store_risk_scores(scan_id, results)
        if store_ok:
            test_pass("store_risk_scores() succeeded")
        else:
            test_fail("store_risk_scores() succeeded")

        # Retrieve via DB method
        rows = dbh.getRiskScores(scan_id)
        if len(rows) == len(results):
            test_pass("getRiskScores() returned correct count",
                      f"expected={len(results)}, got={len(rows)}")
        else:
            test_fail("getRiskScores() returned correct count",
                      f"expected={len(results)}, got={len(rows)}")

        # Verify first row has expected fields
        if rows:
            r = rows[0]
            if len(r) >= 14:
                test_pass("DB row has all 14 columns")
            else:
                test_fail("DB row has all 14 columns", f"got {len(r)} columns")

            # risk_score should match what we stored
            db_score = r[5]
            original = results[0]['risk_score']
            if abs(db_score - original) < 0.01:
                test_pass("Stored risk_score matches original",
                          f"db={db_score}, original={original}")
            else:
                test_fail("Stored risk_score matches original",
                          f"db={db_score}, original={original}")

        # Filter by risk level
        some_level = results[0]['risk_level']
        filtered = dbh.getRiskScores(scan_id, riskLevel=some_level)
        expected_count = sum(1 for e in results if e['risk_level'] == some_level)
        if len(filtered) == expected_count:
            test_pass(f"Level filter '{some_level}' correct count",
                      f"got={len(filtered)}")
        else:
            test_fail(f"Level filter '{some_level}' correct count",
                      f"expected={expected_count}, got={len(filtered)}")

        # Delete
        del_ok = dbh.deleteRiskScores(scan_id)
        if del_ok:
            test_pass("deleteRiskScores() succeeded")
        else:
            test_fail("deleteRiskScores() succeeded")

        # Verify deletion
        after_del = dbh.getRiskScores(scan_id)
        if len(after_del) == 0:
            test_pass("After deletion, getRiskScores() returns empty")
        else:
            test_fail("After deletion, getRiskScores() returns empty",
                      f"got {len(after_del)} rows")

    except Exception as e:
        test_fail("Test execution", str(e))
        traceback.print_exc()
    finally:
        try:
            os.remove(tmpfile)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════
#  TEST 4: Edge cases
# ═══════════════════════════════════════════════════════════════════════
def test_edge_cases():
    header("TEST 4: Edge Cases")
    dbh, tmpfile = create_test_db()

    try:
        # ── 4a: Empty scan ─────────────────────────────────────────────
        scan_id_empty = "test-scan-004a"
        create_scan(dbh, scan_id_empty, "Empty Scan", "empty.com")

        scorer = EntityRiskScorer(dbh)
        results = scorer.score_all_entities(scan_id_empty)
        if results == []:
            test_pass("Empty scan returns empty list")
        else:
            test_fail("Empty scan returns empty list", f"got {len(results)} results")

        # ── 4b: Single entity, no children ─────────────────────────────
        scan_id_single = "test-scan-004b"
        create_scan(dbh, scan_id_single, "Single Entity", "single.com")

        root_hash = make_hash("ROOT_SINGLE")
        insert_event(dbh, scan_id_single, root_hash, "ROOT", "single.com")
        ent_hash = make_hash("only_entity")
        insert_event(dbh, scan_id_single, ent_hash, "DOMAIN_NAME", "single.com",
                     source_hash=root_hash)

        results = scorer.score_all_entities(scan_id_single)
        if len(results) == 1:
            test_pass("Single entity scan returns 1 result")
        else:
            test_fail("Single entity scan returns 1 result", f"got {len(results)}")

        if results and results[0]['risk_level'] in ('INFO', 'LOW'):
            test_pass("Single clean entity has low/info risk",
                      f"level={results[0]['risk_level']}, score={results[0]['risk_score']}")
        elif results:
            test_fail("Single clean entity has low/info risk",
                      f"level={results[0]['risk_level']}, score={results[0]['risk_score']}")

        # ── 4c: All-malicious entity ───────────────────────────────────
        scan_id_mal = "test-scan-004c"
        create_scan(dbh, scan_id_mal, "All Malicious", "evil.com")

        root_hash = make_hash("ROOT_MAL")
        insert_event(dbh, scan_id_mal, root_hash, "ROOT", "evil.com")

        evil_hash = make_hash("evil_ip")
        insert_event(dbh, scan_id_mal, evil_hash, "IP_ADDRESS", "6.6.6.6",
                     source_hash=root_hash)

        # Add lots of malicious + vuln + exposure signals
        mal_types = [
            "MALICIOUS_IPADDR", "BLACKLISTED_IPADDR", "MALICIOUS_INTERNET_NAME",
            "VULNERABILITY_CVE_CRITICAL", "VULNERABILITY_CVE_HIGH",
            "PASSWORD_COMPROMISED", "EMAILADDR_COMPROMISED",
            "SSL_CERTIFICATE_EXPIRED", "SSL_CERTIFICATE_MISMATCH",
            "DARKNET_MENTION_URL", "LEAKSITE_URL",
        ]
        for i, mt in enumerate(mal_types):
            insert_event(dbh, scan_id_mal, make_hash(f"evil_child_{i}"), mt,
                         f"Signal {i}", source_hash=evil_hash)

        results = scorer.score_all_entities(scan_id_mal)
        if results:
            evil = results[0]
            if evil['risk_score'] >= 60:
                test_pass("Heavily malicious entity has HIGH+ risk",
                          f"score={evil['risk_score']}, level={evil['risk_level']}")
            else:
                test_fail("Heavily malicious entity has HIGH+ risk",
                          f"score={evil['risk_score']}, level={evil['risk_level']}")

            # Score capped at 100
            if evil['risk_score'] <= 100:
                test_pass("Risk score capped at 100")
            else:
                test_fail("Risk score capped at 100", f"got {evil['risk_score']}")
        else:
            test_fail("All-malicious scan returned results")

        # ── 4d: Non-scoreable entity types ignored ─────────────────────
        scan_id_ns = "test-scan-004d"
        create_scan(dbh, scan_id_ns, "Non-Scoreable", "ns.com")

        root_hash = make_hash("ROOT_NS")
        insert_event(dbh, scan_id_ns, root_hash, "ROOT", "ns.com")
        insert_event(dbh, scan_id_ns, make_hash("internal_1"), "PROVIDER_DNS",
                     "8.8.8.8", source_hash=root_hash)
        insert_event(dbh, scan_id_ns, make_hash("internal_2"), "RAW_RIR_DATA",
                     "rir data", source_hash=root_hash)

        results = scorer.score_all_entities(scan_id_ns)
        if len(results) == 0:
            test_pass("Non-scoreable event types produce no scored entities")
        else:
            test_fail("Non-scoreable event types produce no scored entities",
                      f"got {len(results)} entities")

    except Exception as e:
        test_fail("Test execution", str(e))
        traceback.print_exc()
    finally:
        try:
            os.remove(tmpfile)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════
#  TEST 5: Scan-level summary aggregation
# ═══════════════════════════════════════════════════════════════════════
def test_summary_aggregation():
    header("TEST 5: Scan-Level Summary Aggregation")
    dbh, tmpfile = create_test_db()

    try:
        scan_id = "test-scan-005"
        create_scan(dbh, scan_id, "Summary Test", "summary.com")

        root_hash = make_hash("ROOT_SUM")
        insert_event(dbh, scan_id, root_hash, "ROOT", "summary.com")

        # Create 10 entities with varying risk profiles
        for i in range(10):
            h = make_hash(f"sum_ent_{i}")
            insert_event(dbh, scan_id, h, "IP_ADDRESS", f"172.16.{i}.1",
                         source_hash=root_hash)

            # Add escalating threat levels
            if i >= 7:
                insert_event(dbh, scan_id, make_hash(f"sum_mal_{i}"),
                             "MALICIOUS_IPADDR", f"Critical {i}", source_hash=h)
                insert_event(dbh, scan_id, make_hash(f"sum_vuln_{i}"),
                             "VULNERABILITY_CVE_CRITICAL", f"CVE {i}", source_hash=h)
            elif i >= 4:
                insert_event(dbh, scan_id, make_hash(f"sum_bl_{i}"),
                             "BLACKLISTED_IPADDR", f"Blacklist {i}", source_hash=h)

        scorer = EntityRiskScorer(dbh)
        results = scorer.score_all_entities(scan_id)
        summary = scorer.get_scan_risk_summary(results)

        # Summary structure
        required_keys = ['total_entities', 'overall_risk_score', 'overall_risk_level',
                         'risk_distribution', 'dimension_averages', 'top_5_entities']
        all_keys = all(k in summary for k in required_keys)
        if all_keys:
            test_pass("Summary contains all required keys")
        else:
            missing = [k for k in required_keys if k not in summary]
            test_fail("Summary contains all required keys", f"missing: {missing}")

        # Total entities
        if summary['total_entities'] == len(results):
            test_pass("total_entities matches scored count",
                      f"count={summary['total_entities']}")
        else:
            test_fail("total_entities matches scored count")

        # Overall risk score is average
        manual_avg = round(sum(e['risk_score'] for e in results) / len(results), 2)
        if abs(summary['overall_risk_score'] - manual_avg) < 0.1:
            test_pass("overall_risk_score = mean of all scores",
                      f"summary={summary['overall_risk_score']}, manual={manual_avg}")
        else:
            test_fail("overall_risk_score = mean of all scores",
                      f"summary={summary['overall_risk_score']}, manual={manual_avg}")

        # Risk distribution sums to total
        dist = summary['risk_distribution']
        dist_total = sum(dist.values())
        if dist_total == summary['total_entities']:
            test_pass("Risk distribution sums to total_entities",
                      f"distribution={dict(dist)}")
        else:
            test_fail("Risk distribution sums to total_entities",
                      f"dist_sum={dist_total}, total={summary['total_entities']}")

        # Top 5 entities
        top5 = summary['top_5_entities']
        if len(top5) == min(5, len(results)):
            test_pass("top_5_entities has correct count",
                      f"count={len(top5)}")
        else:
            test_fail("top_5_entities has correct count")

        # Top 5 should be sorted descending
        top5_scores = [e['risk_score'] for e in top5]
        if top5_scores == sorted(top5_scores, reverse=True):
            test_pass("top_5_entities sorted descending by risk_score")
        else:
            test_fail("top_5_entities sorted descending by risk_score")

        # Dimension averages should all be >= 0
        dim_avgs = summary['dimension_averages']
        if all(v >= 0 for v in dim_avgs.values()):
            test_pass("All dimension averages are non-negative",
                      f"averages={dim_avgs}")
        else:
            test_fail("All dimension averages are non-negative")

        # Empty summary
        empty_summary = scorer.get_scan_risk_summary([])
        if empty_summary['total_entities'] == 0 and empty_summary['overall_risk_score'] == 0.0:
            test_pass("Empty list produces zero-valued summary")
        else:
            test_fail("Empty list produces zero-valued summary")

    except Exception as e:
        test_fail("Test execution", str(e))
        traceback.print_exc()
    finally:
        try:
            os.remove(tmpfile)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"\n{BOLD}{'=' * 70}{RESET}")
    print(f"{BOLD}  PRISM Risk Scoring Engine — Comprehensive Test Suite{RESET}")
    print(f"{BOLD}{'=' * 70}{RESET}")
    print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Python: {sys.version.split()[0]}")
    print()

    test_basic_scoring()
    test_dimension_scoring()
    test_database_integration()
    test_edge_cases()
    test_summary_aggregation()

    # ── Final Report ───────────────────────────────────────────────────
    print(f"\n{BOLD}{'═' * 70}{RESET}")
    total = passed + failed
    if failed == 0:
        print(f"  {GREEN}{BOLD}ALL {total} TESTS PASSED ✓{RESET}")
    else:
        print(f"  {RED}{BOLD}{failed} of {total} TESTS FAILED ✗{RESET}")
    print(f"  {GREEN}Passed: {passed}{RESET}  {RED}Failed: {failed}{RESET}")
    print(f"{BOLD}{'═' * 70}{RESET}\n")

    sys.exit(0 if failed == 0 else 1)
