#!/usr/bin/env python3
import sqlite3
import os

DB_PATH = "/home/ned/iamcalledned/data/sniffer.db"

def reset_articles_table():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] DB file not found at: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("[DB] Dropping old articles table...")
    cursor.execute("DROP TABLE IF EXISTS articles")

    print("[DB] Recreating articles table with fresh schema...")
    cursor.execute('''
        CREATE TABLE articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT,
            url VARCHAR(1000) UNIQUE,
            source VARCHAR(255),
            snippet TEXT,
            full_text TEXT,
            timestamp DATETIME,
            score INT DEFAULT 0,
            bot_response TEXT,
            tags TEXT,
            retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("[DB] Table reset complete.")

if __name__ == "__main__":
    reset_articles_table()
