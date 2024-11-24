from difflib import SequenceMatcher
from datetime import datetime
from search_module import preprocess_text

def calculate_contextual_relevance(query, news_item, user_history, user_location, current_date):
    query = preprocess_text(query)
    title = preprocess_text(news_item['title'])
    summary = preprocess_text(news_item['summary'])
    content = preprocess_text(news_item['content'])

    exact_title_match = 5 if query in title else 0
    exact_summary_match = 3 if query in summary else 0
    exact_content_match = 1 if query in content else 0

    partial_match_score = 0
    partial_match_score += SequenceMatcher(None, query, title).ratio() * 5
    partial_match_score += SequenceMatcher(None, query, summary).ratio() * 3
    partial_match_score += SequenceMatcher(None, query, content).ratio() * 1

    history_score = sum(2 for past_query in user_history if past_query in title or past_query in content)
    location_score = 3 if user_location == news_item.get("location", "") else 0

    news_date = datetime.strptime(news_item["date"], "%Y-%m-%d")
    date_difference = abs((current_date - news_date).days)
    date_score = 3 if date_difference <= 3 else 0

    relevance_score = (
        exact_title_match + exact_summary_match + exact_content_match +
        partial_match_score + history_score + location_score + date_score
    )
    return relevance_score

def contextual_search(query, news_data, user_history=None, user_location=None, current_date=None):
    if user_history is None:
        user_history = []
    if current_date is None:
        current_date = datetime.now()

    query = preprocess_text(query)
    results = []

    for news_item in news_data:
        relevance = calculate_contextual_relevance(query, news_item, user_history, user_location, current_date)
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
