from flask import Flask, request, jsonify
from news_agent import analyze_sentiment
import os
from rss_fetcher import fetch_rss_articles

app = Flask(__name__)

# This app should only be called internally
# Bind your Gunicorn server to 127.0.0.1 when deploying

@app.route("/internal/analyze", methods=["POST"])
def internal_analyze():
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    query = data["query"]
    print(f"[MarketInterpreter] Received query: {query}")

    try:
        result = analyze_sentiment(query)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/internal/fetch_rss_news", methods=["POST"])
def trigger_rss_fetch():
    try:
        articles = fetch_rss_articles()
        return jsonify({
            "status": "RSS fetch complete",
            "articles_fetched": len(articles)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)