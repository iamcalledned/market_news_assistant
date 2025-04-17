#!/usr/bin/env python3
import sqlite3
import argparse
from collections import Counter
import re

DB_PATH = "/home/ned/iamcalledned/data/sniffer.db"

def get_source_counts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT source, COUNT(*) as count
        FROM articles
        GROUP BY source
        ORDER BY count DESC
    """)
    for source, count in cursor.fetchall():
        print(f"{source}: {count} articles")
    conn.close()

def get_recent_by_source(limit=7):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.source, a.headline, a.timestamp
        FROM articles a
        WHERE (
            SELECT COUNT(*)
            FROM articles b
            WHERE b.source = a.source AND b.timestamp >= a.timestamp
        ) <= ?
        ORDER BY a.source, a.timestamp DESC
    """, (limit,))
    current_source = None
    for source, headline, timestamp in cursor.fetchall():
        if source != current_source:
            print(f"\n📰 {source}")
            current_source = source
        print(f"• [{timestamp}] {headline}")
    conn.close()

def get_tag_counts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tags
        FROM articles
        WHERE tags IS NOT NULL AND tags != ''
    """)
    tag_counter = Counter()
    for (tag_str,) in cursor.fetchall():
        try:
            tags = re.findall(r'"([^"]+)"', tag_str)
            if not tags:
                tags = [t.strip() for t in tag_str.split(",")]
            for tag in tags:
                tag_counter[tag.strip()] += 1
        except Exception as e:
            print(f"[WARN] Could not parse tags: {e}")
    print("\n🧠 Tag Counts:")
    for tag, count in tag_counter.most_common():
        print(f"{tag}: {count}")
    conn.close()

def inspect_text_quality(limit=20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT source, headline, LENGTH(full_text), full_text
        FROM articles
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    for source, headline, length, text in cursor.fetchall():
        print(f"\n🔹 Source: {source}\n📰 Headline: {headline}\n📏 Length: {length}")
        print("🧪 Snippet Preview:\n", text[:300].replace("\n", " ") + "...")
    conn.close()

def find_empty_articles():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT source, headline, url
        FROM articles
        WHERE LENGTH(full_text) < 100
        ORDER BY timestamp DESC
        LIMIT 20
    """)
    for source, headline, url in cursor.fetchall():
        print(f"🚨 {source} - {headline}\n🔗 {url}\n")
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="News DB Debugging CLI")
    parser.add_argument("--tags", action="store_true", help="Show tag counts")
    parser.add_argument("--sources", action="store_true", help="Show article counts by source")
    parser.add_argument("--recent", action="store_true", help="Show recent articles by source")
    parser.add_argument("--inspect-text", action="store_true", help="Inspect text quality of recent articles")
    parser.add_argument("--find-empty", action="store_true", help="Find articles with empty or short content")
    args = parser.parse_args()

    if args.tags:
        get_tag_counts()
    if args.sources:
        get_source_counts()
    if args.recent:
        get_recent_by_source()
    if args.inspect_text:
        inspect_text_quality()
    if args.find_empty:
        find_empty_articles()

    if not any(vars(args).values()):
        parser.print_help()

if __name__ == "__main__":
    main()
# python3 debug_tools.py --tags           # Tag count summary
# python3 debug_tools.py --sources        # Count by source
# python3 debug_tools.py --recent         # 7 most recent per source
# python3 debug_tools.py --inspect-text   # Text length + preview
# python3 debug_tools.py --find-empty     # Flag empty/broken full_text articles