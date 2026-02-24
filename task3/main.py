# Михеева Полина Александровна, 11-209
# Галеева Камилла Маратовна, 11-209

import collections
import pymorphy3

INDEX_FILE = '../task1/index.txt'
INVERTED_INDEX_FILE = './inverted_index.txt'

ENCODING = 'utf-8'

OPERATORS = {'and', 'or', 'not'}
PRIORITY = {
    'not': 3,
    'and': 2,
    'or': 1
}

def load_indexes():
    inverted_index = collections.defaultdict(set)
    all_docs = set()

    with open(INVERTED_INDEX_FILE, encoding=ENCODING) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) > 1:
                lemma = parts[0]
                docs = set(parts[1:])
                inverted_index[lemma] = docs
                all_docs |= docs

    urls = {}
    with open(INDEX_FILE, encoding=ENCODING) as f:
        for line in f:
            doc_id, url = line.strip().split()
            urls[doc_id] = url

    return inverted_index, urls, all_docs

def normalize_word(morph, word):
    return morph.parse(word)[0].normal_form

def tokenize_query(query):
    query = query.replace('(', ' ( ').replace(')', ' ) ')
    return query.lower().split()

def to_rpn(tokens):
    output = []
    stack = []

    for token in tokens:
        if token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        elif token in OPERATORS:
            while (
                stack and stack[-1] in OPERATORS and
                PRIORITY[stack[-1]] >= PRIORITY[token]
            ):
                output.append(stack.pop())
            stack.append(token)
        else:
            output.append(token)

    while stack:
        output.append(stack.pop())

    return output

def evaluate_rpn(rpn, inverted_index, all_docs):
    stack = []

    for token in rpn:
        if token == 'and':
            b = stack.pop()
            a = stack.pop()
            stack.append(a & b)
        elif token == 'or':
            b = stack.pop()
            a = stack.pop()
            stack.append(a | b)
        elif token == 'not':
            a = stack.pop()
            stack.append(all_docs - a)
        else:
            stack.append(inverted_index.get(token, set()))

    return stack[0] if stack else set()

def search(query, morph, inverted_index, all_docs):
    tokens = tokenize_query(query)

    normalized = []
    for token in tokens:
        if token in OPERATORS or token in {'(', ')'}:
            normalized.append(token)
        else:
            normalized.append(normalize_word(morph, token))

    rpn = to_rpn(normalized)
    return evaluate_rpn(rpn, inverted_index, all_docs)

def main():
    inverted_index, urls, all_docs = load_indexes()
    morph = pymorphy3.MorphAnalyzer()

    while True:
        query = input('Введите запрос (или exit): ')
        if query.lower() == 'exit':
            break

        result_docs = search(query, morph, inverted_index, all_docs)

        if not result_docs:
            print('Ничего не найдено')
        else:
            for doc_id in sorted(result_docs):
                print(urls.get(doc_id, doc_id))

if __name__ == '__main__':
    main()