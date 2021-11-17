from bs4 import BeautifulSoup
import requests
import re
import os
from pathlib import Path
import configparser
import sys


config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

ARGS = sys.argv[1:]
base_url = 'https://www.zeit.de/index'
download_folder = os.path.expanduser(config.get('general', 'download_folder'))
url_lock_folder = os.path.expanduser(config.get('general', 'url_lock_folder'))
session = requests.session()


class ArticleNotParsableError(Exception):
    """Exception raised for errors while parsing the article text.

    Attributes:
        data_name -- data name that could not be parsed
        message -- explanation of the error
    """

    def __init__(self, data_name, url):
        message = f'WARNING: could not parse the data item "{data_name}" in article at: {url}'
        super().__init__(message)


def main():
    if ARGS:
        deal_article(ARGS[0])
        return
    articles = get_articles_from_index()
    for article in articles:
        deal_article(article['href'])


def get_articles_from_index():
    response = session.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.select('article > a.zon-teaser-standard__faux-link, article > a.zon-teaser-lead__faux-link, article > a.zon-teaser-poster__faux-link')
    return articles


def deal_article(url):
    if url_locked(url):
        return
    if article_type_is_excluded(url):
        return
    final_url = get_final_article_url(url)
    print(final_url)
    response = session.get(final_url)
    try:
        datestring, title = get_article_data(response)
    except ArticleNotParsableError as e:
        print(e, file=sys.stderr)
        lock_url(url)
        print('INFO: even though locked url for now')
        return
    target_folder = prepare_target_folder(datestring)
    filename = make_filename(datestring, title)
    save_article(target_folder, filename, response.text)
    lock_url(url)


def url_locked(url: str) -> bool:
    return os.path.exists(make_url_lock_filepath(url))


def make_url_lock_filepath(url: str) -> str:
    filepath = os.path.join(url_lock_folder, url.replace('/', '_'))
    return filepath


def article_type_is_excluded(url: str) -> bool:
    if not url.startswith('https://www.zeit.de'):
        return True
    if url.startswith('https://www.zeit.de/zett'):
        return True


def get_final_article_url(url):
    head = requests.head(url + '/komplettansicht')
    if head.status_code == 200:
        return url + '/komplettansicht'
    return url


def get_article_data(response) -> tuple:
    soup = BeautifulSoup(response.content, 'html.parser')
    datestring = soup.select('time.metadata__date:nth-child(1), .meta__date')
    if not datestring:
        raise ArticleNotParsableError('datestring', response.url)
    datestring = datestring[0]['datetime']
    title = soup.select('.article-heading__title, .headline__title, .article-header__title')
    if not title:
        raise ArticleNotParsableError('title', response.url)
    title = title[0].text
    title = re.sub(r'[\s\W]', '_', title)
    return datestring, title


def make_filename(datestring, title):
    filename = f'{datestring}__{title}.html'
    return filename


def prepare_target_folder(datestring: str) -> str:
    month_folder = datestring.split('-')
    month_folder = f'{month_folder[0]}-{month_folder[1]}'
    month_folder = os.path.join(download_folder, month_folder)
    assure_folderpath(month_folder)
    return month_folder


def save_article(folder: str, filename: str, text: str):
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w') as file:
        file.write(text)
    print('->', filepath)


def lock_url(url: str) -> None:
    assure_folderpath(url_lock_folder)
    url_filepath = make_url_lock_filepath(url)
    Path(url_filepath).touch()


def assure_folderpath(folder_path: str) -> None:
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


if __name__ == '__main__':
    main()
