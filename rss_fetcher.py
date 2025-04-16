import feedparser
from datetime import datetime
from newspaper import Article
from database import insert_articles
from rss_config import RSS_FEEDS

def fetch_full_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text, article.title
    except Exception as e:
        print(f"[RSS] Failed to fetch full text from {url}: {e}")
        return "", "Untitled"

def fetch_rss_articles():
    all_articles = []

    for source, feed_url in RSS_FEEDS.items():
        print(f"[RSS] Fetching feed from {source}...")
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            url = entry.get("link")
            timestamp = entry.get("published", datetime.utcnow().isoformat())
            snippet = entry.get("summary", "")
            full_text, headline = fetch_full_text(url)

            article_data = {
                "headline": headline.strip()[:500],
                "url": url,
                "source": source,
                "snippet": snippet.strip()[:500],
                "full_text": full_text.strip(),
                "timestamp": timestamp
            }

            all_articles.append(article_data)

    insert_articles(all_articles)
    return all_articles

if __name__ == "__main__":
    fetch_rss_articles()
