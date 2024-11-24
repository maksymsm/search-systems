import json
import re
from difflib import SequenceMatcher

def load_news_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def preprocess_text(text):
    return re.sub(r'[^\w\s]', '', text.lower())

# Calculate relevance based on phrase matching
def calculate_phrase_relevance(query, news_item):
    query = preprocess_text(query)
    title = preprocess_text(news_item['title'])
    summary = preprocess_text(news_item['summary'])
    content = preprocess_text(news_item['content'])

    # Exact phrase match scores
    exact_title_match = 5 if query in title else 0
    exact_summary_match = 3 if query in summary else 0
    exact_content_match = 1 if query in content else 0

    # Partial phrase matching using SequenceMatcher
    partial_match_score = 0
    partial_match_score += SequenceMatcher(None, query, title).ratio() * 5
    partial_match_score += SequenceMatcher(None, query, summary).ratio() * 3
    partial_match_score += SequenceMatcher(None, query, content).ratio() * 1

    # Total relevance score
    relevance_score = (
        exact_title_match + exact_summary_match + exact_content_match + partial_match_score
    )
    return relevance_score

def phrase_search(query, news_data):
    query = preprocess_text(query)
    results = []

    for news_item in news_data:
        relevance = calculate_phrase_relevance(query, news_item)
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

def cli_phrase_search(news_data):
    print("Welcome to the Phrase-Based News Search System!")
    
    while True:
        query = input("\nEnter your search query (or type 'exit' to quit): ").strip()
        if query.lower() == 'exit':
            print("\nThank you for using the system. Goodbye!")
            break
        
        results = phrase_search(query, news_data)
        
        print("\nTop results:")
        if results:
            for i, result in enumerate(results[:5], start=1):  # Top 5 results
                print(f"{i}. [{result['category']}] {result['title']} ({result['date']}, {result['location']}) - Relevance: {result['relevance']:.2f}")
                print(f"   Summary: {result['summary']}")
                print(f"   Content: {result['content']}\n")
        else:
            print("No results found.")

if __name__ == "__main__":
    file_path = "news_database.json"
    news_data = load_news_data(file_path)
    
    cli_phrase_search(news_data)
