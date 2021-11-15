# ZeitLos

This is a scraper for articles on **Zeit Online** (https://zeit.de). It does simply 
scrape all articles that are published on the frontpage and stores them as `.html` 
files to a `download_folder`. Only the source file, without external files (images 
etc) are downloaded. 

Already scraped urls will not be loaded again. 

## Installation

### Pipenv

```
$ pipenv install
$ pipenv run python main.py
```

### Pip

```
$ pip install -r requirements.txt
$ python3.6 main.py
```

## Configuration

Use the example config file to set up your own config
```
$ mv config.ini.example config.ini
```

and set your prefered folders
```
[general]
download_folder = ~/downloads/zeitlos
url_lock_folder = ~/downloads/zeitlos/.url_locks
```
folders that are configured here, will automatically be created.


## Automatisation

You can just set up a cronjob to regularly run the tool and download all new articles.

```
$ crontab -l
*/30 * * * * python3.6 ~/bin/zeitlos/main.py > /dev/null
```

## Disclaimer

Please note, that you need to have the permission from **Zeit Online** to scrape 
their websites automatically. You also should have paid for **Zeit+** because with 
this scraping tool you would be able to download articles before they are put behind 
the Paywall. 