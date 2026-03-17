# Михеева Полина Александровна, 11-209
# Галеева Камилла Маратовна, 11-209

import os
import math
from collections import defaultdict, Counter
import pymorphy3
import re

LEMMAS_DIR = "../task4/lemmas"

morph = pymorphy3.MorphAnalyzer()

def load_document_vectors():
    document_vectors = {}

    for file_name in os.listdir(LEMMAS_DIR):

        if not file_name.startswith("выкачка_"):
            continue

        file_path = os.path.join(LEMMAS_DIR, file_name)

        term_weights = {}

        with open(file_path, "r", encoding="utf-8") as file:

            for line in file:

                parts = line.strip().split()

                if len(parts) != 3:
                    continue

                term = parts[0]
                tfidf = float(parts[2])

                term_weights[term] = tfidf

        document_vectors[file_name] = term_weights

    return document_vectors


def preprocess_query(query):

    tokens = []

    for word in query.lower().split():

        word = re.sub(r"[^а-яa-z]", "", word)

        if not word:
            continue

        lemma = morph.parse(word)[0].normal_form

        tokens.append(lemma)

    return tokens


def compute_document_frequency(document_vectors):

    df = defaultdict(int)

    for vector in document_vectors.values():

        for term in vector.keys():
            df[term] += 1

    return df


def create_query_vector(query_tokens, document_vectors, df):

    N = len(document_vectors)

    term_counts = Counter(query_tokens)

    query_vector = {}

    for term, tf in term_counts.items():

        if term not in df:
            continue

        idf = math.log(N / (1 + df[term]))

        query_vector[term] = tf * idf

    return query_vector


def cosine_similarity(vec1, vec2):

    dot_product = 0

    for term in vec1:
        dot_product += vec1[term] * vec2.get(term, 0)

    norm1 = math.sqrt(sum(v * v for v in vec1.values()))
    norm2 = math.sqrt(sum(v * v for v in vec2.values()))

    if norm1 == 0 or norm2 == 0:
        return 0

    return dot_product / (norm1 * norm2)


def search(query, document_vectors, df):

    tokens = preprocess_query(query)

    query_vector = create_query_vector(tokens, document_vectors, df)

    scores = {}

    for doc, vector in document_vectors.items():

        sim = cosine_similarity(query_vector, vector)

        scores[doc] = sim

    results = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return results


def main():
    document_vectors = load_document_vectors()

    df = compute_document_frequency(document_vectors)

    print("Введите q для выхода\n")

    while True:

        query = input("Ваш запрос: ").strip()

        if query.lower() == "q":
            break

        results = search(query, document_vectors, df)

        printed = False

        for doc, score in results:
            if score != 0:
                print(doc)
                printed = True

        if not printed:
            print("результатов не найдено")

if __name__ == "__main__":
    main()