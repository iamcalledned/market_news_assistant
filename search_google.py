import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

def search_headlines(query, num_results=5):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": num_results
    }

    res = requests.get(url, params=params)
    res.raise_for_status()
    data = res.json()

    results = []
    for item in data.get("items", []):
        results.append({
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "url": item.get("link"),
            "source": item.get("displayLink"),
            "timestamp": datetime.utcnow().isoformat()
        })

    return results
