import re
from difflib import SequenceMatcher

def preprocess_text(text):
    return re.sub(r'[^\w\s]', '', text.lower())

def calculate_relevance(query, news_item):
    query = preprocess_text(query)
    title = preprocess_text(news_item['title'])
    summary = preprocess_text(news_item['summary'])
    content = preprocess_text(news_item['content'])

    query_words = query.split()
    title_match_count = sum(title.count(word) for word in query_words)
    summary_match_count = sum(summary.count(word) for word in query_words)
    content_match_count = sum(content.count(word) for word in query_words)

    partial_match_score = 0
    partial_match_score += SequenceMatcher(None, query, title).ratio() * 5
    partial_match_score += SequenceMatcher(None, query, summary).ratio() * 3
    partial_match_score += SequenceMatcher(None, query, content).ratio() * 1

    relevance_score = (
        (title_match_count * 3) + (summary_match_count * 2) +
        content_match_count + partial_match_score
    )
    return relevance_score

def basic_search(query, news_data):
    query = preprocess_text(query)
    results = []

    for news_item in news_data:
        relevance = calculate_relevance(query, news_item)
        if relevance > 0:
            results.append({
                "category": news_item["category"],
                "title": news_item["title"],
                "date": news_item["date"],
                "location": news_item["location"],
                "summary": news_item["summary"],
                "content": news_item["content"],
                "relevance": relevance
            })

    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results
