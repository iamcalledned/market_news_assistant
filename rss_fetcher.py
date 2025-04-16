import feedparser
from datetime import datetime
from bs4 import BeautifulSoup
from newspaper import Article
from playwright.sync_api import sync_playwright
import time
from database import insert_articles
from rss_config import RSS_FEEDS

def fetch_full_text_with_playwright(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                java_script_enabled=True,
            )
            page = context.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
            time.sleep(4)
            html = page.content()
            browser.close()

            soup = BeautifulSoup(html, "html.parser")
            article = soup.find("article") or soup.find("main") or soup.body
            text = article.get_text(separator="\n", strip=True) if article else soup.get_text()
            return text, "Untitled"
    except Exception as e:
        print(f"[Playwright] Failed on {url}: {e}")
        return "", "Untitled"

def fetch_full_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text, article.title
    except Exception as e:
        print(f"[RSS] Newspaper failed, falling back to Playwright for {url}: {e}")
        return fetch_full_text_with_playwright(url)

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