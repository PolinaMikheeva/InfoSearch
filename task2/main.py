# Михеева Полина Александровна, 11-209
# Галеева Камилла Маратовна, 11-209

import os
import re
import collections
import ssl
import nltk
import pymorphy3
from bs4 import BeautifulSoup

SOURCE_DIR = '../task1/pages'
TOKENS_DIR = './tokens'
LEMMAS_DIR = './lemmas'

ENCODING = 'utf-8'
LANG_RUSSIAN = 'russian'

def extract_text_from_html(file_path):
    with open(file_path, 'r', encoding=ENCODING) as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
        return ' '.join(soup.stripped_strings)

# токенизация, лемматизация и фильтрация
def process_text_data(text, tokenizer, stop_words_set, morph_analyzer):
    valid_tokens = set()
    token_lemmas = collections.defaultdict(set)

    tokens_in_text = tokenizer.tokenize(text)

    for token in tokens_in_text:
        lower_token = token.lower()
        if len(lower_token) < 2 or lower_token in stop_words_set:
            continue

        parsed_token = morph_analyzer.parse(lower_token)
        is_digit = bool(re.fullmatch(r'\d+', lower_token))
        is_russian = bool(re.fullmatch(r'[а-яА-Я]{2,}', lower_token))

        if not is_russian or is_digit:
            continue

        valid_tokens.add(lower_token)
        if parsed_token[0].score >= 0.5:
            token_lemmas[parsed_token[0].normal_form].add(lower_token)

    return valid_tokens, token_lemmas

# сохранение токенов и лемм
def save_tokens_and_lemmas(tokens_set, lemmas_dict, file_name):
    os.makedirs(TOKENS_DIR, exist_ok=True)
    os.makedirs(LEMMAS_DIR, exist_ok=True)

    tokens_file = os.path.join(TOKENS_DIR, f'{file_name}.txt')
    lemmas_file = os.path.join(LEMMAS_DIR, f'{file_name}.txt')

    with open(tokens_file, 'w', encoding=ENCODING) as token_file:
        token_file.write('\n'.join(sorted(tokens_set)) + '\n')

    with open(lemmas_file, 'w', encoding=ENCODING) as lemma_file:
        for lemma, tokens in sorted(lemmas_dict.items()):
            lemma_file.write(f'{lemma} {" ".join(sorted(tokens))}\n')

def main():
    ssl._create_default_https_context = ssl._create_unverified_context

    nltk.download('stopwords')

    stop_words = set(nltk.corpus.stopwords.words(LANG_RUSSIAN))
    tokenizer = nltk.tokenize.WordPunctTokenizer()
    morph_analyzer = pymorphy3.MorphAnalyzer()

    for file_name in os.listdir(SOURCE_DIR):
        file_path = os.path.join(SOURCE_DIR, file_name)

        if not file_name.endswith('.html'):
            continue

        text = extract_text_from_html(file_path)
        tokens, lemmas = process_text_data(text, tokenizer, stop_words, morph_analyzer)

        base_name = os.path.splitext(file_name)[0]
        save_tokens_and_lemmas(tokens, lemmas, base_name)

if __name__ == '__main__':
    main()
