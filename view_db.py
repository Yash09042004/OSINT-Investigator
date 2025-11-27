#!/usr/bin/env python3
"""
PRISM Database Viewer - Quick view of database contents
"""

import sqlite3
import os

# Check multiple possible locations
DB_PATHS = [
    "spiderfoot.db",
    os.path.expanduser("~/.spiderfoot/spiderfoot.db"),
    "/var/lib/spiderfoot/spiderfoot.db",
    "/var/lib/prism/spiderfoot.db"
]

def find_db():
    for path in DB_PATHS:
        if os.path.exists(path):
            return path
    return None

def main():
    DB_PATH = find_db()
    
    if not DB_PATH:
        print("\n❌ Database not found!")
        print("   Run a scan first to create the database.")
        print("   Checked:")
        for p in DB_PATHS:
            print(f"   - {p}")
        return
    
    print(f"\n📁 DB: {DB_PATH} ({os.path.getsize(DB_PATH)/1024:.1f} KB)\n")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Tables
    print("═" * 50)
    print("📋 TABLES")
    print("═" * 50)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for t in cur.fetchall():
        cur.execute(f"SELECT COUNT(*) FROM {t[0]}")
        print(f"  {t[0]}: {cur.fetchone()[0]} rows")
    
    # Scans
    print("\n" + "═" * 50)
    print("🔍 SCANS")
    print("═" * 50)
    try:
        cur.execute("SELECT name, seed_target, status FROM tbl_scan_instance ORDER BY created DESC LIMIT 5")
        rows = cur.fetchall()
        if rows:
            for r in rows:
                print(f"  • {r[0][:20]} | {r[1][:25]} | {r[2]}")
        else:
            print("  No scans yet.")
    except: print("  No scans.")
    
    # Top events
    print("\n" + "═" * 50)
    print("📊 TOP EVENTS")
    print("═" * 50)
    try:
        cur.execute("SELECT type, COUNT(*) FROM tbl_scan_results GROUP BY type ORDER BY COUNT(*) DESC LIMIT 8")
        rows = cur.fetchall()
        if rows:
            for r in rows:
                print(f"  {r[0]}: {r[1]}")
        else:
            print("  No events yet.")
    except: print("  No events.")
    
    # Sample data
    print("\n" + "═" * 50)
    print("📄 SAMPLE DATA (Latest 10)")
    print("═" * 50)
    try:
        cur.execute("SELECT type, substr(data,1,50), module FROM tbl_scan_results ORDER BY generated DESC LIMIT 10")
        rows = cur.fetchall()
        if rows:
            for r in rows:
                data = r[1].replace('\n', ' ')[:45] if r[1] else "N/A"
                print(f"  [{r[0][:20]}] {data}...")
        else:
            print("  No data yet.")
    except: print("  No data.")
    
    # Correlations
    print("\n" + "═" * 50)
    print("🔗 CORRELATIONS")
    print("═" * 50)
    try:
        cur.execute("SELECT title, rule_risk FROM tbl_scan_correlation_results LIMIT 5")
        rows = cur.fetchall()
        if rows:
            for r in rows:
                print(f"  [{r[1]}] {r[0][:40]}")
        else:
            print("  No correlations yet.")
    except: print("  No correlations.")
    
    conn.close()
    print("\n" + "═" * 50)
    print("💡 sqlite3 " + DB_PATH + " for raw SQL")
    print("═" * 50 + "\n")

if __name__ == "__main__":
    main()
