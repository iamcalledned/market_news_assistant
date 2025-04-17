#!/usr/bin/env python3
import sqlite3

DB_PATH = "/home/ned/iamcalledned/data/sniffer.db"

def get_source():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT source, COUNT(*) as count
        FROM articles
        GROUP BY source
        ORDER BY count DESC
    """)

    results = cursor.fetchall()
    for source, count in results:
        print(f"{source}: {count} articles")

    conn.close()
#!/usr/bin/env python3
import sqlite3

def add_tags_column():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE articles ADD COLUMN tags TEXT")
        print("[DB] 'tags' column added to articles table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("[DB] 'tags' column already exists.")
        else:
            raise
    conn.commit()
    conn.close()

def get_counts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.source, a.headline, a.timestamp
        FROM articles a
        WHERE (
            SELECT COUNT(*)
            FROM articles b
            WHERE b.source = a.source AND b.timestamp >= a.timestamp
        ) <= 7
        ORDER BY a.source, a.timestamp DESC
    """)

    results = cursor.fetchall()
    current_source = None
    for source, headline, timestamp in results:
        if source != current_source:
            print(f"\n📰 {source}")
            current_source = source
        print(f"• [{timestamp}] {headline}")

    conn.close()

def get_tag_counts():
    import sqlite3
    from collections import Counter
    import re

    DB_PATH = "/home/ned/iamcalledned/data/sniffer.db"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT bot_response
        FROM articles
        WHERE bot_response IS NOT NULL AND bot_response != ''
    """)

    tag_counter = Counter()

    for (response,) in cursor.fetchall():
        try:
            tags = re.findall(r'"([^"]+)"', response)
            for tag in tags:
                tag_counter[tag.strip()] += 1
        except Exception as e:
            print(f"[WARN] Could not parse tags from response: {e}")

    print("🧠 Tag Counts:")
    for tag, count in tag_counter.most_common():
        print(f"{tag}: {count}")

    conn.close()


if __name__ == "__main__":
    get_tag_counts()

