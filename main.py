from bs4 import BeautifulSoup
import requests
import re
import os


url = 'https://www.zeit.de/index'
download_folder = '_work/downloads'
session = requests.session()
response = session.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
articles = soup.select('article > a.zon-teaser-standard__faux-link, article > a.zon-teaser-lead__faux-link')
for article in articles:
    url = article['href']
    if not url.startswith('https://www.zeit.de'):
        continue
    if url.startswith('https://www.zeit.de/zett'):
        continue
    response = session.get(url)
    print(response.url)
    soup = BeautifulSoup(response.content, 'html.parser')
    datestring = soup.select('time.metadata__date:nth-child(1), .meta__date')[0]['datetime']
    title = soup.select('.article-heading__title, .headline__title, .article-header__title')[0].text
    title = re.sub(r'[\s\W]', '_', title)
    filename = f'{datestring}__{title}.html'
    with open(os.path.join(download_folder, filename), "w") as file:
        file.write(response.text)
