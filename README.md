# Books parser from tululu.org
This project allows you to parse books from [tululu.org](https://tululu.org/). It downloads books and books covers, also create JSON file with all downloaded books data.

## How to install
Python3 should be already installed. Then use pip (or pip3, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```

## How to run a script
Parsing books:
```
python main.py --start_page 1 --end_page 2
```
## Arguments

1. `-si` or `--start_page` – *required argument* – Which page to start downloading from.
2. `-ep` or `--end_page` – *required argument* – To which page to continue downloading
3. `-df` or `--dest_folder` – The path to the directory with the parsing results
4. `-si` or `--skip_imgs` – Don't download pictures
5. `-st` or `--skip_txts` – Don't download books
6. `-jn` or `--json_name` – Specify your *.json filename
