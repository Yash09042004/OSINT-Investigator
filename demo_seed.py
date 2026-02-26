#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
demo_seed.py  —  PRISM OSINT Demo Data Seeder
=============================================
Creates a synthetic high-risk scan in the PRISM database so you can
showcase graph analysis, risk scoring, and correlation features.

Usage:
    python3 demo_seed.py

The script creates a scan named "DEMO - APT Threat Actor Investigation"
targeting the seed "apt29-infrastructure.net" and inserts ~50 realistic
OSINT results covering:

  • Malicious IPs linked to known threat actors
  • Blacklisted / typosquat domains
  • Leaked credentials and email addresses
  • C2 infrastructure nodes (high-degree → HIGH anomaly)
  • Bitcoin wallets and dark-web mentions
  • Vulnerability and exploit references

After running, open the GUI → Graph Analysis, select the "DEMO" scan
and click "Build Graph & Run Analysis".  Then go to Risk Analysis and
click "Run Risk Analysis" on the same scan.
"""

import sqlite3
import hashlib
import time
import json
import random
import string
import os
import sys

import os
DB_PATH = os.path.expanduser("~/.spiderfoot/spiderfoot.db")


def guid():
    """Generate a short random hex ID."""
    return hashlib.md5(
        (str(time.time()) + "".join(random.choices(string.ascii_uppercase, k=6))).encode()
    ).hexdigest()[:8].upper()


def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()


def main():
    if not os.path.exists(DB_PATH):
        print(f"[!] Database not found at {DB_PATH}. Run sf.py first.", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ── Create the scan instance ──────────────────────────────────────
    scan_id   = "DEMO" + guid()[:4]
    scan_name = "DEMO - APT Threat Actor Investigation"
    seed      = "apt29-infrastructure.net"
    now       = int(time.time())

    cur.execute("DELETE FROM tbl_scan_instance WHERE name = ?", (scan_name,))
    cur.execute("""
        INSERT INTO tbl_scan_instance
            (guid, name, seed_target, created, started, ended, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (scan_id, scan_name, seed, now, now, now + 120, "FINISHED"))
    conn.commit()
    print(f"[+] Created scan: {scan_name}  (ID={scan_id})")

    # ── Seed event data ───────────────────────────────────────────────
    # Format: (type, data, module, source_event_hash, confidence)
    # source_event_hash = None → ROOT
    ROOT = "ROOT"

    events = [
        # === Domains / DNS === (seed + aliases)
        ("INTERNET_NAME",    seed,                          "sfp_dnsresolve",   ROOT, 100),
        ("INTERNET_NAME",    "c2-panel.apt29-infrastructure.net", "sfp_dnsresolve", ROOT, 95),
        ("INTERNET_NAME",    "exfil.apt29-infrastructure.net",    "sfp_dnsresolve", ROOT, 95),
        ("INTERNET_NAME",    "update-service.ru",           "sfp_similardomain", ROOT, 85),
        ("INTERNET_NAME",    "microsofft-update.com",       "sfp_similardomain", ROOT, 80),
        ("INTERNET_NAME",    "windowss-defender.net",       "sfp_similardomain", ROOT, 80),
        ("DOMAIN_NAME",      "apt29-infrastructure.net",    "sfp_dnsresolve",   ROOT, 100),
        ("DOMAIN_NAME",      "darknode-relay.onion.ly",     "sfp_dnsresolve",   ROOT, 90),

        # === Malicious / Blacklisted IPs (C2 infrastructure) ===
        ("IP_ADDRESS",       "185.220.101.47",  "sfp_dnsresolve",   sha256(seed), 100),
        ("IP_ADDRESS",       "185.220.101.48",  "sfp_dnsresolve",   sha256(seed), 100),
        ("IP_ADDRESS",       "185.220.101.50",  "sfp_dnsresolve",   sha256(seed), 100),
        ("IP_ADDRESS",       "195.181.160.111", "sfp_dnsresolve",   sha256(seed), 95),
        ("IP_ADDRESS",       "91.108.4.168",    "sfp_dnsresolve",   sha256(seed), 90),
        ("IP_ADDRESS",       "10.0.0.1",        "sfp_dnsresolve",   sha256(seed), 50),
        ("MALICIOUS_IPADDR", "185.220.101.47 - TorExitNode/GreyNoise/ThreatList", "sfp_abuseipdb", sha256("185.220.101.47"), 95),
        ("MALICIOUS_IPADDR", "185.220.101.48 - KnownMalware/C2", "sfp_abuseipdb", sha256("185.220.101.48"), 98),
        ("MALICIOUS_IPADDR", "195.181.160.111 - RansomwareC2",   "sfp_abuseipdb", sha256("195.181.160.111"), 92),
        ("MALICIOUS_IPADDR", "91.108.4.168 - APT29/Cozy Bear",   "sfp_abuseipdb", sha256("91.108.4.168"),   99),

        # === Malicious domains ===
        ("MALICIOUS_INTERNET_NAME", "microsofft-update.com - PhishTank",       "sfp_phishtank",     sha256("microsofft-update.com"),  92),
        ("MALICIOUS_INTERNET_NAME", "windowss-defender.net - OpenPhish",       "sfp_phishtank",     sha256("windowss-defender.net"),  88),
        ("MALICIOUS_INTERNET_NAME", "c2-panel.apt29-infrastructure.net - MDRC","sfp_malwaredomains", sha256("c2-panel.apt29-infrastructure.net"), 97),
        ("MALICIOUS_INTERNET_NAME", "darknode-relay.onion.ly - TorHiddenSvc", "sfp_malwaredomains", sha256("darknode-relay.onion.ly"), 90),

        # === Email addresses / credential leaks ===
        ("EMAILADDR",        "admin@apt29-infrastructure.net",   "sfp_hunter",    sha256(seed), 85),
        ("EMAILADDR",        "root@update-service.ru",           "sfp_hunter",    sha256(seed), 80),
        ("EMAILADDR",        "ops@microsofft-update.com",        "sfp_hunter",    sha256("microsofft-update.com"), 80),
        ("EMAILADDR",        "exfil.collector@protonmail.com",   "sfp_hunter",    sha256(seed), 75),
        ("LEAKSITE_CONTENT", "admin@apt29-infrastructure.net:P@ssw0rd123! (HaveIBeenPwned)", "sfp_haveibeenpwned", sha256("admin@apt29-infrastructure.net"), 90),
        ("LEAKSITE_CONTENT", "root@update-service.ru:S3cr3tK3y! (BreachCompilation)", "sfp_haveibeenpwned", sha256("root@update-service.ru"), 85),
        ("PASSWORD_USED",    "P@ssw0rd123!",  "sfp_haveibeenpwned", sha256("admin@apt29-infrastructure.net"), 80),

        # === Humans / WHOIS ===
        ("HUMAN_NAME",       "Ivan Petrov",    "sfp_whois",   sha256(seed),      75),
        ("HUMAN_NAME",       "Dmitri Volkov",  "sfp_whois",   sha256(seed),      70),
        ("PHONE_NUMBER",     "+7-495-555-0192","sfp_whois",   sha256(seed),      65),
        ("PHYSICAL_ADDRESS", "ul. Lenina 42, Moscow, Russia 123456", "sfp_whois", sha256(seed), 70),

        # === Dark web / TOR ===
        ("DARKWEB_MENTION",  "apt29-infrastructure.net mentioned on AlphaBay listing with RaaS kit", "sfp_darkowl", sha256(seed), 88),
        ("DARKWEB_MENTION",  "exfil.apt29-infrastructure.net listed as active C2 endpoint",          "sfp_darkowl", sha256(seed), 92),

        # === Crypto wallets ===
        ("BITCOIN_ADDRESS",  "1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf", "sfp_bitcoin_find", sha256("ops@microsofft-update.com"), 70),
        ("BITCOIN_ADDRESS",  "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy", "sfp_bitcoin_find", sha256(seed), 68),

        # === Vulnerabilities ===
        ("VULNERABILITY_CVE", "CVE-2021-34527 (PrintNightmare) - exploited on 185.220.101.47", "sfp_vuln", sha256("185.220.101.47"), 95),
        ("VULNERABILITY_CVE", "CVE-2023-23397 (Outlook 0-day) - linked to domain exfiltration", "sfp_vuln", sha256(seed), 95),
        ("VULNERABILITY_CVE", "CVE-2020-1472 (Zerologon) - lateral movement indicator",         "sfp_vuln", sha256("195.181.160.111"), 90),

        # === Affiliates / co-hosted domains ===
        ("AFFILIATE_INTERNET_NAME", "steal-creds-login.com",     "sfp_similar",  sha256(seed), 75),
        ("AFFILIATE_INTERNET_NAME", "secure-banking-verify.net",  "sfp_similar",  sha256(seed), 72),
        ("AFFILIATE_IPADDR",        "185.220.101.49",             "sfp_ipinfo",   sha256("185.220.101.47"), 80),

        # === SSL / Certificates ===
        ("SSL_CERTIFICATE_ISSUED", "CN=apt29-infrastructure.net, OU=IT, O=Shell Corp, C=RU", "sfp_ssl", sha256(seed), 85),
        ("SSL_CERTIFICATE_MISMATCH","CN=microsofft-update.com does not match microsoft.com", "sfp_ssl", sha256("microsofft-update.com"), 90),

        # === Social / Passive ===
        ("USERNAME",         "apt_operator_29",  "sfp_accounts",  sha256("admin@apt29-infrastructure.net"), 60),
        ("SOCIAL_MEDIA",     "Telegram @apt_relay_bot linked to C2 comms",         "sfp_telegram", sha256(seed), 72),
    ]

    # Build a hash map: (type+data) → hash  so we can use source hashes
    existing_hashes = {ROOT: ROOT}

    inserted = 0
    for ev_type, ev_data, module, src_hash, confidence in events:
        h = sha256(ev_type + ev_data)
        existing_hashes[ev_data] = h

        # resolve source hash: if src_hash is a data string, look up its actual hash
        if src_hash in existing_hashes:
            actual_src = existing_hashes[src_hash]
        else:
            actual_src = src_hash  # fallback (keep as-is)

        ts = int(time.time() * 1000)
        try:
            cur.execute("""
                INSERT INTO tbl_scan_results
                    (scan_instance_id, hash, type, generated, confidence,
                     visibility, risk, module, data, false_positive, source_event_hash)
                VALUES (?, ?, ?, ?, ?, 1, 0, ?, ?, 0, ?)
            """, (scan_id, h, ev_type, ts, confidence, module, ev_data, actual_src))
            inserted += 1
        except sqlite3.IntegrityError:
            pass  # duplicate hash → skip


    conn.commit()
    print(f"[+] Inserted {inserted} OSINT events into scan {scan_id}")

    # ── Summary ───────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("  DEMO SCAN READY")
    print("=" * 60)
    print(f"  Scan name : {scan_name}")
    print(f"  Scan ID   : {scan_id}")
    print(f"  Seed      : {seed}")
    print(f"  Events    : {inserted}")
    print()
    print("  Next steps:")
    print("  1. Open http://127.0.0.1:5001/graphanalysis")
    print(f"     → Select '{scan_name}'")
    print("     → Click 'Build Graph & Run Analysis'")
    print()
    print("  2. Open http://127.0.0.1:5001/riskanalysis")
    print(f"     → Select '{scan_name}'")
    print("     → Click 'Run Risk Analysis'")
    print("=" * 60)

    conn.close()


if __name__ == "__main__":
    main()
