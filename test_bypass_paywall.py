#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

def fetch_wsj_article_via_archive(url):
    archived_url = f"https://archive.ph/newest/{url}"
    print(f"[WSJ Bypass] Trying archived URL: {archived_url}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                java_script_enabled=True,
            )
            page = context.new_page()
            page.goto(archived_url, timeout=60000)
            page.wait_for_load_state("networkidle")
            time.sleep(6)
            html = page.content()
            browser.close()

            soup = BeautifulSoup(html, "html.parser")
            article = soup.find("body")
            text = article.get_text(separator="\n", strip=True) if article else ""
            return text[:500]  # return preview

    except Exception as e:
        print(f"[WSJ Bypass] Failed to fetch archived WSJ article: {e}")
        return ""

if __name__ == "__main__":
    test_url = "https://www.wsj.com/articles/nikkei-may-rise-as-weak-yen-raises-earnings-hopes-776a8056"
    preview = fetch_wsj_article_via_archive(test_url)
    print("\n🧾 Article Preview:\n", preview)
