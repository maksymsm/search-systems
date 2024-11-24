from datetime import datetime
from search_module import basic_search
from contextual_module import contextual_search

def cli_interface(news_data):
    print("Welcome to the News Search System!")

    user_history = []  # Initialize history for contextual search

    while True:
        mode = input("\nChoose search mode (1: Basic, 2: Contextual, 'exit' to quit): ").strip()
        if mode.lower() == 'exit':
            print("\nThank you for using the system. Goodbye!")
            break
        
        query = input("\nEnter your search query: ").strip()

        if mode == '1':
            results = basic_search(query, news_data)
        elif mode == '2':
            user_location = input("\nEnter your location (e.g., Київ, Львів, Одеса): ").strip()
            current_date = datetime.now()
            results = contextual_search(query, news_data, user_history, user_location, current_date)
            user_history.append(query)  # Add query to history
        else:
            print("Invalid option. Please choose 1 or 2.")
            continue

        print("\nTop results:")
        if results:
            for i, result in enumerate(results[:5], start=1):  # Top 5 results
                print(f"{i}. [{result['category']}] {result['title']} ({result['date']}, {result['location']}) - Relevance: {result['relevance']:.2f}")
                print(f"   Summary: {result['summary']}")
                print(f"   Content: {result['content']}\n")
        else:
            print("No results found.")
