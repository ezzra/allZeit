# all-zeit

This is a downloader for articles on **Zeit Online** (https://zeit.de). It does simply 
download all articles that show up in the feed and store them as `.html` 
files to a `download_folder`. Only the source file, without external files (images 
etc) are downloaded. 

Already downloaded urls will not be loaded again. 

## Downloading

```
$ git clone https://github.com/ezzra/allzeit ~/bin/allzeit
```

## Installation

### Pipenv

```
$ pipenv install
$ pipenv run python main.py
```

### Pip

```
$ pip install -r requirements.txt
```

## Configuration

Use the example config file to set up your own config
```
$ mv config.ini.example config.ini
```

and set your prefered folder
```
[general]
download_folder = ~/html
```
folders that are configured here, will automatically be created.


## Web access with .htaccess

With each run the tool will assure that there is a `download_folder/.htaccess`. 
If not so, the file `htaccess.example` will be copied there and rewrite urls to the 
`*.html` files.


## First run

```
$ python3.6 main.py
```

## Automatisation

You can just set up a cronjob to regularly run the tool and download all new articles.

```
$ crontab -l
*/30 * * * * python3.6 ~/bin/allzeit/main.py > /dev/null
```

## DISCLAIMER

Please note, that you need to have the permission from **Zeit Online** to download from 
their websites automatically. You should also have paid for **Zeit+** because with 
this downloading tool you would be able to store and read articles before they are put 
behind the Paywall. 