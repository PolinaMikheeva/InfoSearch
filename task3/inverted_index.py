# Михеева Полина Александровна, 11-209
# Галеева Камилла Маратовна, 11-209

import collections
import nltk
import os
import re
import pymorphy3
from bs4 import BeautifulSoup

SOURCE_DIR = '../task1/pages'
INVERTED_INDEX_FILE = './inverted_index.txt'

ENCODING = 'utf-8'
LANG_RUSSIAN = 'russian'

EXCLUDED_POS = {
    'NUMB', 'ROMN', 'PNCT',
    'PREP', 'CONJ', 'PRCL', 'INTJ',
    'LATN', 'UNKN'
}

def extract_doc_id(filename: str) -> str:
    digits = ''.join(filter(str.isdigit, filename))
    if not digits:
        raise ValueError(f'Не удалось извлечь doc_id из имени файла: {filename}')
    return digits

def extract_texts_from_html(directory):
    texts = {}

    for filename in os.listdir(directory):
        if not filename.endswith('.html'):
            continue

        doc_id = extract_doc_id(filename)
        path = os.path.join(directory, filename)

        with open(path, encoding=ENCODING) as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            texts[doc_id] = ' '.join(soup.stripped_strings)

    return texts

def build_inverted_index(directory, tokenizer, stop_words, morph):
    inverted_index = collections.defaultdict(set)

    texts = extract_texts_from_html(directory)

    for doc_id, text in texts.items():
        tokens = tokenizer.tokenize(text)

        for token in tokens:
            token = token.lower()

            if len(token) < 2:
                continue
            if token in stop_words:
                continue
            if not re.fullmatch(r'[а-яё]+', token):
                continue

            parsed = morph.parse(token)[0]

            if parsed.tag.POS in EXCLUDED_POS:
                continue

            lemma = parsed.normal_form
            inverted_index[lemma].add(doc_id)

    return inverted_index

def save_inverted_index(inverted_index, filename):
    with open(filename, 'w', encoding=ENCODING) as f:
        for lemma in sorted(inverted_index.keys()):
            docs = ' '.join(sorted(inverted_index[lemma], key=int))
            f.write(f'{lemma} {docs}\n')

def main():
    nltk.download('stopwords')

    stop_words = set(nltk.corpus.stopwords.words(LANG_RUSSIAN))
    tokenizer = nltk.tokenize.WordPunctTokenizer()
    morph = pymorphy3.MorphAnalyzer()

    inverted_index = build_inverted_index(
        SOURCE_DIR,
        tokenizer,
        stop_words,
        morph
    )

    save_inverted_index(inverted_index, INVERTED_INDEX_FILE)

if __name__ == '__main__':
    main()