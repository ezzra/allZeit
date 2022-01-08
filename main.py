import requests
import os
from pathlib import Path
import configparser
import sys
import feedparser
from time import mktime
from datetime import datetime
from collections import namedtuple
from typing import List
from urllib.parse import urlparse
from pathlib import PurePosixPath
from shutil import copyfile


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


Article = namedtuple('Article', 'url image title summary published')
Articles = List[Article]


def main():
    assure_folderpath(download_folder)
    assure_htaccess()
    if ARGS:
        deal_article(ARGS[0])
        return
    articles = get_articles_from_feed()
    for article in articles:
        deal_article(article)


def get_articles_from_feed() -> Articles:
    NewsFeed = feedparser.parse("https://newsfeed.zeit.de")
    articles = list()
    for entry in NewsFeed['entries']:
        article = parse_feed_item(entry)
        articles.append(article)
    return articles


def parse_feed_item(entry: feedparser.FeedParserDict) -> Article:
    published_time = datetime.fromtimestamp(mktime(entry['published_parsed']))
    if len(entry['links']) > 1:
        image = entry['links'][1]['href']
    else:
        image = None
    article = Article(entry['link'], image, entry['title'], entry['summary'], published_time)
    return article


def deal_article(article: Article):
    if url_locked(article.url):
        return
    if article_type_is_excluded(article):
        return
    filepath = get_filepath_from_url(article.url)
    save_article(article.url, filepath)
    lock_url(article.url)


def url_locked(url: str) -> bool:
    return os.path.exists(make_url_lock_filepath(url))


def make_url_lock_filepath(url: str) -> str:
    filepath = os.path.join(url_lock_folder, url.replace('/', '_'))
    return filepath


def article_type_is_excluded(article: Article) -> bool:
    if not article.url.startswith('https://www.zeit.de'):
        return True
    if article.url.startswith('https://www.zeit.de/zett'):
        return True
    if article.url.startswith('https://www.zeit.de/video'):
        return True


def get_final_article_url(url):
    head = requests.head(url + '/komplettansicht')
    if head.status_code == 200:
        return url + '/komplettansicht'
    return url


def prepare_target_folder(url_path) -> str:
    folder_path = os.path.join(download_folder, *url_path[:-1])
    print(folder_path)
    assure_folderpath(folder_path)
    return folder_path


def get_filepath_from_url(url):
    url_path = urlparse(url).path
    path = PurePosixPath(url_path).parts[1:]
    if path[-1] == 'komplettansicht':
        path = path[:1]
    folder_path = path[:-1]
    filename = path[-1] + '.html'
    return os.path.join(*folder_path, filename)


def save_article(article_url: str, filepath: str):
    final_url = get_final_article_url(article_url)
    response = session.get(final_url)
    final_filepath = os.path.join(download_folder, filepath)
    assure_folderpath(os.path.dirname(final_filepath))
    with open(final_filepath, 'w') as file:
        file.write(response.text)
    print(final_url)
    print('->', filepath)


def lock_url(url: str) -> None:
    assure_folderpath(url_lock_folder)
    url_filepath = make_url_lock_filepath(url)
    Path(url_filepath).touch()


def assure_folderpath(folder_path: str) -> None:
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def assure_htaccess():
    htaccess_path = os.path.join(download_folder, '.htaccess')
    if os.path.exists(htaccess_path):
        return
    example_htaccess_path = os.path.join(os.path.dirname(__file__), 'htaccess.example')
    copyfile(example_htaccess_path, htaccess_path)


if __name__ == '__main__':
    main()
