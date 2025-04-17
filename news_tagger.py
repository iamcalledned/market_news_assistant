import os
import json
import sqlite3
import re
import nltk
import csv


from nltk.corpus import stopwords

# Download required resources if needed
try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("punkt")
    nltk.download("stopwords")

# Load config file
with open("nlp_config.json", "r") as f:
    config = json.load(f)

DB_PATH = config["db_path"]
TAG_KEYWORDS = config["tag_keywords"]

stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    tokens = nltk.word_tokenize(text.lower())
    return " ".join([word for word in tokens if word not in stop_words])

def tag_article(text):
    tags = set()
    cleaned = clean_text(text)
    for tag, keywords in TAG_KEYWORDS.items():
        if any(kw in cleaned for kw in keywords):
            tags.add(tag)
    return ",".join(sorted(tags))

def add_tags_column():
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

    for aid, headline, snippet, full_text, source in articles:
        combined = " ".join(filter(None, [headline, snippet, full_text]))
        tags = tag_article(combined)
        c.execute("UPDATE articles SET tags = ? WHERE id = ?", (tags, aid))
        output_rows.append([headline or "", source or "", snippet or "", tags])
        updated += 1

    conn.commit()
    conn.close()
    print(f"[Tagger] Tagged {updated} articles.")
    save_tagging_output(output_rows)


def save_tagging_output(tagged_data, filename="tagged_articles_output.csv"):
    with open(filename, mode="w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["headline", "source", "snippet", "tags"])
        for row in tagged_data:
            writer.writerow(row)
    print(f"[Output] Saved tagging results to {filename}")



def run_tagger():
    add_tags_column()
    tag_all_articles()

if __name__ == "__main__":
    run_tagger()
