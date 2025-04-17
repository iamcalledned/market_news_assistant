import os
import json
import sqlite3
import csv
import re

from flashtext import KeywordProcessor
import nltk
from nltk.corpus import stopwords

# Ensure NLTK requirements
try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("punkt")
    nltk.download("stopwords")

# Load config
with open("nlp_config.json", "r") as f:
    config = json.load(f)

DB_PATH = config["db_path"]
TAG_KEYWORDS = config["tag_keywords"]
stop_words = set(stopwords.words("english"))

# Initialize FlashText keyword processor
keyword_processor = KeywordProcessor()
for tag, keywords in TAG_KEYWORDS.items():
    for kw in keywords:
        keyword_processor.add_keyword(kw.lower(), tag)

def clean_text(text):
    """Basic text cleanup and stopword removal."""
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    tokens = text.lower().split()
    return " ".join([word for word in tokens if word not in stop_words])

def tag_article(text):
    """Return a comma-separated list of tags found in the article."""
    cleaned = clean_text(text)
    found_tags = keyword_processor.extract_keywords(cleaned)
    return ",".join(sorted(set(found_tags)))

def add_tags_column():
    print("[DEBUG] DB path:", DB_PATH)
    print("[DEBUG] File exists?", os.path.exists(DB_PATH))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE articles ADD COLUMN tags TEXT")
        print("[DB] 'tags' column added.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("[DB] 'tags' column already exists.")
        else:
            raise
    conn.commit()
    conn.close()

def tag_all_articles():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, headline, snippet, full_text, source FROM articles")
    articles = c.fetchall()

    updated = 0
    output_rows = []
    no_tag_rows = []

    for aid, headline, snippet, full_text, source in articles:
        combined = " ".join(filter(None, [headline, snippet, full_text]))
        tags = tag_article(combined)
        c.execute("UPDATE articles SET tags = ? WHERE id = ?", (tags, aid))
        output_rows.append([headline or "", source or "", snippet or "", tags])
        if not tags:
            no_tag_rows.append([aid, headline or "", source or "", snippet or ""])
        updated += 1

    conn.commit()
    conn.close()

    print(f"[Tagger] Tagged {updated} articles.")
    save_tagging_output(output_rows)
    if no_tag_rows:
        save_no_tag_log(no_tag_rows)

def save_tagging_output(tagged_data, filename="tagged_articles_output.csv"):
    with open(filename, mode="w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["headline", "source", "snippet", "tags"])
        for row in tagged_data:
            writer.writerow(row)
    print(f"[Output] Saved tagging results to {filename}")

def save_no_tag_log(no_tags, filename="no_tags_log.csv"):
    with open(filename, mode="w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id", "headline", "source", "snippet"])
        for row in no_tags:
            writer.writerow(row)
    print(f"[Warning] Saved {len(no_tags)} untagged articles to {filename}")

def run_tagger():
    add_tags_column()
    tag_all_articles()

if __name__ == "__main__":
    run_tagger()
