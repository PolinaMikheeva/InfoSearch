import os
import time
import requests
from zipfile import ZipFile
from bs4 import BeautifulSoup
from datetime import date, timedelta
from urllib.parse import urljoin

BASE_URL = 'https://www.ixbt.com'
START_DATE = date(2026, 2, 12)
PAGES_NEEDED = 100

HTML_FOLDER = 'pages'
INDEX_FILE = 'index.txt'
ZIP_FILE = 'выкачка.zip'
ENCODING = 'utf-8'

REQUEST_TIMEOUT = 10
REQUEST_DELAY = 0.5

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; educational-crawler/1.0)'
}

UNWANTED_TAGS = ['script', 'style', 'img', 'iframe', 'noscript', 'svg']

# сбор ссылок
def collect_links():
    links = []
    seen = set()
    current_date = START_DATE

    while len(links) < PAGES_NEEDED:
        section = f'/news/{current_date.year}/{current_date.month:02d}/{current_date.day:02d}'
        url = BASE_URL + section

        try:
            response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        except requests.RequestException:
            current_date -= timedelta(days=1)
            continue

        if response.status_code != 200:
            current_date -= timedelta(days=1)
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        for a in soup.find_all('a', href=True):
            href = a['href']

            if href.startswith(section) and href.endswith('.html'):
                full_url = urljoin(BASE_URL, href)

                if full_url not in seen:
                    seen.add(full_url)
                    links.append(full_url)

            if len(links) >= PAGES_NEEDED:
                break

        current_date -= timedelta(days=1)
        time.sleep(REQUEST_DELAY)

    return links

# удаление внешних ресурсов
def remove_external_resources(html):
    soup = BeautifulSoup(html, 'html.parser')

    for link in soup.find_all('link', rel='stylesheet'):
        link.extract()

    for tag in UNWANTED_TAGS:
        for unwanted in soup.find_all(tag):
            unwanted.extract()

    for tag in soup.find_all(True):
        if 'style' in tag.attrs:
            del tag.attrs['style']

    return str(soup)

# создание страниц
def save_pages(links):
    os.makedirs(HTML_FOLDER, exist_ok=True)

    with open(INDEX_FILE, 'w', encoding=ENCODING) as index_file:
        for i, url in enumerate(links, start=1):

            try:
                response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            except requests.RequestException:
                continue

            if response.status_code == 200:
                cleaned_html = remove_external_resources(response.text)

                file_path = os.path.join(
                    HTML_FOLDER,
                    f'выкачка_{i}.html'
                )

                with open(file_path, 'w', encoding=ENCODING) as f:
                    f.write(cleaned_html)

                index_file.write(f'{i} {url}\n')

            time.sleep(REQUEST_DELAY)

# создание архива
def make_zip():
    with ZipFile(ZIP_FILE, 'w') as zipf:
        for file in os.listdir(HTML_FOLDER):
            zipf.write(
                os.path.join(HTML_FOLDER, file),
                arcname=file
            )

def main():
    links = collect_links()
    save_pages(links)
    make_zip()

if __name__ == '__main__':
    main()