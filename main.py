import requests
import os
import configparser
import sys
import feedparser
from urllib.parse import urlparse
from pathlib import PurePosixPath
from shutil import copyfile


config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

ARGS = sys.argv[1:]
base_url = 'https://www.zeit.de/index'
download_folder = os.path.expanduser(config.get('general', 'download_folder'))
session = requests.session()


def main():
    assure_folderpath(download_folder)
    assure_htaccess()
    if ARGS:
        process_article(ARGS[0])
        return
    urls = get_urls_from_feed()
    for url in urls:
        process_article(url)


def get_urls_from_feed() -> list:
    NewsFeed = feedparser.parse("https://newsfeed.zeit.de")
    urls = list()
    for entry in NewsFeed['entries']:
        urls.append(entry['link'])
    return urls


def process_article(url: str):
    if article_type_is_excluded(url):
        return
    filepath = get_filepath_from_url(url)
    if os.path.exists(os.path.join(download_folder, filepath)):
        return
    save_article(url, filepath)


def article_type_is_excluded(url) -> bool:
    if not url.startswith('https://www.zeit.de'):
        return True
    if url.startswith('https://www.zeit.de/zett'):
        return True
    if url.startswith('https://www.zeit.de/video'):
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
