# Михеева Полина Александровна, 11-209
# Галеева Камилла Маратовна, 11-209

import os
import math
import collections
import nltk
import pymorphy3
from bs4 import BeautifulSoup

SOURCE_DIR = "../task1/pages"
TOKENS_DIR = "./tokens"
LEMMAS_DIR = "./lemmas"

ENCODING = "utf-8"
LANG = "russian"

EXCLUDED_TAGS = {
    'NUMB', 'ROMN', 'PNCT', 'PREP', 'CONJ', 'PRCL', 'INTJ', 'LATN', 'UNKN'
}

tokenizer = nltk.tokenize.WordPunctTokenizer()
stop_words = set(nltk.corpus.stopwords.words(LANG))
morph = pymorphy3.MorphAnalyzer()


def extract_texts_from_html(directory):
    texts = {}

    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)

        index = int(''.join(filter(str.isdigit, filename)))

        with open(path, "r", encoding=ENCODING) as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            text = " ".join(soup.stripped_strings)

        texts[index] = text

    return texts


def process_text(text):
    tokens = []
    lemma_map = collections.defaultdict(list)

    for token in tokenizer.tokenize(text.lower()):

        if len(token) < 2 or token in stop_words:
            continue

        parsed = morph.parse(token)[0]

        if any(tag in parsed.tag for tag in EXCLUDED_TAGS):
            continue

        tokens.append(token)
        lemma_map[parsed.normal_form].append(token)

    return tokens, lemma_map


def compute_idf(doc_tokens):
    N = len(doc_tokens)
    df = collections.Counter()

    for tokens in doc_tokens.values():
        unique_tokens = set(tokens)

        for token in unique_tokens:
            df[token] += 1

    idf = {}

    for token, freq in df.items():
        idf[token] = math.log(N / (1 + freq))

    return idf


def save_results(filename, data):
    with open(filename, "w", encoding=ENCODING) as f:
        for word, idf, tfidf in data:
            f.write(f"{word} {idf:.6f} {tfidf:.6f}\n")


def main():

    os.makedirs(TOKENS_DIR, exist_ok=True)
    os.makedirs(LEMMAS_DIR, exist_ok=True)

    documents = extract_texts_from_html(SOURCE_DIR)

    doc_tokens = {}
    doc_lemmas = {}

    for doc_id, text in documents.items():

        tokens, lemmas = process_text(text)

        doc_tokens[doc_id] = tokens
        doc_lemmas[doc_id] = lemmas

    idf_tokens = compute_idf(doc_tokens)

    for doc_id in sorted(documents.keys()):

        tokens = doc_tokens[doc_id]
        lemmas = doc_lemmas[doc_id]

        token_counts = collections.Counter(tokens)
        total_tokens = len(tokens)

        token_results = []
        lemma_results = []

        for token, count in token_counts.items():

            tf = count / total_tokens
            idf = idf_tokens.get(token, 0)

            tfidf = tf * idf

            token_results.append((token, idf, tfidf))

        for lemma, token_list in lemmas.items():

            count = sum(token_counts[token] for token in token_list)

            lf = count / total_tokens

            idf = idf_tokens.get(lemma, 0)

            lf_idf = lf * idf

            lemma_results.append((lemma, idf, lf_idf))

        save_results(f"{TOKENS_DIR}/выкачка_{doc_id}.txt", token_results)
        save_results(f"{LEMMAS_DIR}/выкачка_{doc_id}.txt", lemma_results)


if __name__ == "__main__":
    main()