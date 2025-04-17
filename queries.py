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

if __name__ == "__main__":
    main()

