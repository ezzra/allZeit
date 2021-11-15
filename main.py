from bs4 import BeautifulSoup
import requests
import re
import os
from pathlib import Path


url = 'https://www.zeit.de/index'
download_folder = '_work/downloads'
path_scraped_urls = os.path.join(download_folder, 'scraped_urls')

session = requests.session()
response = session.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
articles = soup.select('article > a.zon-teaser-standard__faux-link, article > a.zon-teaser-lead__faux-link, article > a.zon-teaser-poster__faux-link')
for article in articles:
    url = article['href']
    if os.path.exists(os.path.join(path_scraped_urls, url.replace('/', '_'))):
        continue
    if not url.startswith('https://www.zeit.de'):
        continue
    if url.startswith('https://www.zeit.de/zett'):
        continue
    head = requests.head(url + '/komplettansicht')
    if head.status_code == 200:
        fulltext_url = url + '/komplettansicht'
    else:
        fulltext_url = url
    response = session.get(fulltext_url)
    print(fulltext_url)

    soup = BeautifulSoup(response.content, 'html.parser')
    datestring = soup.select('time.metadata__date:nth-child(1), .meta__date')[0]['datetime']
    title = soup.select('.article-heading__title, .headline__title, .article-header__title')[0].text
    title = re.sub(r'[\s\W]', '_', title)

    month_folder = datestring.split('-')
    month_folder = f'{month_folder[0]}-{month_folder[1]}'
    month_folder = os.path.join(download_folder, month_folder)
    if not os.path.exists(month_folder):
        os.makedirs(month_folder)
    filename = f'{datestring}__{title}.html'
    with open(os.path.join(month_folder, filename), 'w') as file:
        file.write(response.text)

    if not os.path.exists(path_scraped_urls):
        os.makedirs(path_scraped_urls)
    Path(os.path.join(path_scraped_urls, url.replace('/', '_'))).touch()
