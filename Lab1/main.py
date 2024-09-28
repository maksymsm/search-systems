from inverted_index import build_inverted_index
from search import search

with open('archival_doc.txt', 'r', encoding='utf-8') as file:
    content = file.read().split('\n')

inverted_index = build_inverted_index(content)

# print("Inverted index:", inverted_index)

query = "10,000 Allies in Normandy"

docs_index = search(query, inverted_index)

print(f"Query '{query}' is found in docs: {docs_index}")
