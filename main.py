import argparse
import requests
import json
import urllib3

from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin

from parse_tululu_category import parse_category


DOWNLOAD_URL = 'https://tululu.org/txt.php?id='
INFO_URL = 'https://tululu.org/b'


def get_book_info(url, book_id):
    response = requests.get(f'{url}{book_id}',
                            allow_redirects=False, verify=False)
    response.raise_for_status()

    return response


def download_txt(book_id, filename, folder=f'books/'):
    Path(folder).mkdir(parents=True, exist_ok=True)

    url = f'{DOWNLOAD_URL}{book_id}'

    response = requests.get(url, allow_redirects=False, verify=False)
    response.raise_for_status()

    path_to_save = Path(folder).joinpath(f'{filename}.txt')

    with open(path_to_save, 'wb') as file:
        file.write(response.content)

    return str(path_to_save)


def download_img(book_data, folder=f'images/'):
    Path(folder).mkdir(parents=True, exist_ok=True)

    image_url = parse_img(book_data)

    response = requests.get(image_url, allow_redirects=False, verify=False)
    response.raise_for_status()

    filename = sanitize_filename(image_url.split('/')[-1])

    path_to_save = Path(folder).joinpath(f'{filename}')

    with open(path_to_save, 'wb') as image:
        image.write(response.content)

    return str(path_to_save)


def download_book(start_page, end_page, book_data, title, author, download_images, download_texts):

    book_info = {
        'title': title,
        'author': author,
        'img_path': download_images,
        'book_path': download_texts,
        'comments': parse_comments(book_data),
        'genre': parse_genres(book_data)
    }

    return book_info


def create_json(filename, obj):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(obj, file, ensure_ascii=False)


def parse_genres(book_data):
    soup = BeautifulSoup(book_data.text, 'lxml')
    genre = soup.select_one('span.d_book a').text

    return genre


def parse_comments(book_data):
    soup = BeautifulSoup(book_data.text, 'lxml')
    comments = [comment.select_one(
        'span.black').text for comment in soup.select('div.texts')]

    return comments


def parse_img(book_data):
    soup = BeautifulSoup(book_data.text, 'lxml')
    image_link = soup.select_one('div.bookimage img')['src']

    return urljoin(INFO_URL, image_link)


def parse_title_and_author(book_data):
    soup = BeautifulSoup(book_data.text, 'lxml')

    title_and_author = soup.select_one('h1').text.split('\xa0 :: \xa0')

    title = title_and_author[0].strip()
    author = title_and_author[1].strip()

    return sanitize_filename(title), sanitize_filename(author)


def create_argparse():
    parser = argparse.ArgumentParser(
        description='Download book from tululu.org')

    parser.add_argument(
        '-sp', '--start_page', help='Which page to start downloading from', default=1, type=int)
    parser.add_argument('-ep', '--end_page',
                        help='To which page to start downloading', type=int)
    parser.add_argument('-df', '--dest_folder', default=Path.cwd(),
                        help='The path to the directory with the parsing results', type=str)
    parser.add_argument('-si', '--skip_imgs',
                        help='Don\'t download pictures', action="store_true", type=str)
    parser.add_argument('-st', '--skip_txts',
                        help='Don\'t download books', action="store_true", type=str)
    parser.add_argument(
        '-jn', '--json_name', default='books.json', help='Specify your *.json filename', type=str)
    args = parser.parse_args()

    return parser


def main():
    parser = create_argparse()
    args = parser.parse_args()

    if all([
        args.start_page < args.end_page,
        args.start_page > 0,
        args.end_page > 0 if args.end_page else True
    ]):
        all_books = []
        book_ids = parse_category(args.start_page, args.end_page)

        for book_id in book_ids:
            book_data = get_book_info(INFO_URL, book_id)

            title, author = parse_title_and_author(book_data)

            if args.skip_txts:
                download_texts = None
            else:
                download_texts = download_txt(book_id, title)

            if args.skip_imgs:
                download_images = None
            else:
                download_images = download_img(book_data)

            book_info = download_book(
                args.start_page, args.end_page, book_data, title, author, download_images, download_texts)

            all_books.append(book_info)

        create_json(args.json_name, all_books)
    else:
        print('Incorrect start_page and end_page properties')


if __name__ == '__main__':
    main()
