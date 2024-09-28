from inverted_index import preprocess

def search(query_text, index):
    query_tokens = preprocess(query_text)
    if not query_tokens:
        return set()

    result = index.get(query_tokens[0], set())

    for token in query_tokens[1:]:
        result &= index.get(token, set())

    return result