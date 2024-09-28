import re
import nltk
from collections import defaultdict
from nltk.stem import WordNetLemmatizer

# nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

stop_words = {"the", "is", "in", "and", "or", "on", "with", "a", "an", "it", "of"}


def preprocess(text):
    tokens = re.findall(r'\b\w+\b', text.lower())
    tokens = [word for word in tokens if word not in stop_words]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    return tokens


def build_inverted_index(text):
    preprocessed_documents = [preprocess(doc) for doc in text]

    inverted_index = defaultdict(set)
    for doc_id, doc in enumerate(preprocessed_documents):
        for word in doc:
            inverted_index[word].add(doc_id)

    return inverted_index