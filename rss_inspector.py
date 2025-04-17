import feedparser
from rss_config import RSS_FEEDS
from datetime import datetime
import os

LOG_DIR = "rss_logs"
os.makedirs(LOG_DIR, exist_ok=True)

def inspect_feed_structure():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"rss_inspection_{timestamp}.log")

    with open(log_file, "w", encoding="utf-8") as log:
        for name, url in RSS_FEEDS.items():
            print(f"\n🔍 Inspecting feed: {name}")
            log.write(f"\n🔍 Inspecting feed: {name}\nURL: {url}\n")

            feed = feedparser.parse(url)
            if not feed.entries:
                msg = "❌ No entries found or failed to parse.\n"
                print(msg.strip())
                log.write(msg)
                continue

            entry = feed.entries[0]
            keys = list(entry.keys())
            print(f"✅ Sample entry keys: {keys}")
            log.write(f"✅ Sample entry keys: {keys}\n")

            preview_fields = ['title', 'link', 'summary', 'description', 'published', 'content']
            for field in preview_fields:
                if field in entry:
                    value = str(entry[field])
                    snippet = value[:300].replace("\n", " ").strip()
                    if len(value) > 300:
                        snippet += "..."
                    print(f"  • {field}: {snippet}")
                    log.write(f"  • {field}: {snippet}\n")

            log.write("-" * 80 + "\n")

    print(f"\n📝 Log saved to: {log_file}")

if __name__ == "__main__":
    inspect_feed_structure()
