from interface_module import cli_interface
import json

def load_news_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

if __name__ == "__main__":
    file_path = "news_database.json"
    news_data = load_news_data(file_path)
    cli_interface(news_data)
