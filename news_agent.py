from search_serp import search_headlines
from summarize import summarize_headlines

def analyze_sentiment(query):
    print(f"[MarketInterpreter] Running search for: {query}")
    headlines = search_headlines(query)

    if not headlines:
        return "No relevant headlines found. Cannot provide an analysis."

    print(f"[MarketInterpreter] Retrieved {len(headlines)} headlines")
    summary = summarize_headlines(query, headlines)

    return summary
