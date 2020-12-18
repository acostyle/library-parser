import argparse
import requests
import json

from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin

from exceptions import raise_if_redirect
from parse_tululu_category import parse_category


DOWNLOAD_URL = 'https://tululu.org/txt.php'
INFO_URL = 'https://tululu.org'


def get_book_info(book_url):
    response = requests.get(book_url, allow_redirects=False, verify=False)
    response.raise_for_status()
    raise_if_redirect(response)

    return BeautifulSoup(response.text, 'lxml')


def download_txt(book_url, filename, folder):
    download_id = book_url[book_url.find('/b')+2:-1]

    response = requests.get(DOWNLOAD_URL, params={
                            "id": download_id, }, verify=False)
    response.raise_for_status()
    raise_if_redirect(response)

    path_to_save_txt = Path('books').joinpath(f'{filename}.txt')
    path_to_save = Path(folder).joinpath(path_to_save_txt)

    with open(path_to_save, 'wb') as file:
        file.write(response.content)

    return str(path_to_save_txt)


def download_img(book_data, book_url, folder):
    image_url = parse_img(book_data, book_url)

    response = requests.get(image_url, allow_redirects=False, verify=False)
    response.raise_for_status()
    raise_if_redirect(response)

    filename = sanitize_filename(image_url.split('/')[-1])

    path_to_save_img = Path('images').joinpath(f'{filename}')
    path_to_save = Path(folder).joinpath(path_to_save_img)

    with open(path_to_save, 'wb') as image:
        image.write(response.content)

    return str(path_to_save_img)


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
    soup = book_data.select('span.d_book a')
    genres = [genres.text for genres in soup]
    return genres


def parse_comments(book_data):
    title_tag = book_data.select("div.texts span.black")
    comments = [comment.text for comment in title_tag]
    return comments


def parse_img(book_data, book_url):
    img_src = book_data.select_one('div.bookimage img')['src']
    return urljoin(book_url, img_src)


def parse_title_and_author(book_data):
    header = book_data.select_one("#content")
    title_tag = header.h1
    author, title = title_tag.text.split(' \xa0 :: \xa0 ')

    return sanitize_filename(author), sanitize_filename(title)


def create_argparser():
    parser = argparse.ArgumentParser(
        description='Download book from tululu.org')

    parser.add_argument(
        '-sp', '--start_page', help='Which page to start downloading from', default=1, type=int)
    parser.add_argument('-ep', '--end_page',
                        help='To which page to start downloading', type=int)
    parser.add_argument('-df', '--dest_folder', default=Path.cwd(),
                        help='The path to the directory with the parsing results', type=str)
    parser.add_argument('-si', '--skip_imgs',
                        help='Don\'t download pictures', action="store_true")
    parser.add_argument('-st', '--skip_txts',
                        help='Don\'t download books', action="store_true")
    parser.add_argument(
        '-jn', '--json_name', default='books.json', help='Specify your *.json filename', type=str)

    args = parser.parse_args()

    if not (args.start_page < args.end_page and
            args.start_page > 0 and
            args.end_page > 0):
        print('Incorrect start_page or end_page arguments')

    return parser


def main():
    parser = create_argparser()
    args = parser.parse_args()

    Path(args.dest_folder, 'images').mkdir(parents=True, exist_ok=True)
    Path(args.dest_folder, 'books').mkdir(parents=True, exist_ok=True)

    all_books = []
    book_urls = parse_category(args.start_page, args.end_page)

    for book_url in book_urls:
        try:
            book_data = get_book_info(book_url)
            title, author = parse_title_and_author(book_data)

            download_texts = None
            if not args.skip_txts:
                download_texts = download_txt(
                    book_url, title, args.dest_folder)

            download_images = None
            if not args.skip_imgs:
                download_images = download_img(
                    book_data, book_url, args.dest_folder)

            book_info = download_book(
                args.start_page, args.end_page, book_data, title, author, download_images, download_texts)

            all_books.append(book_info)

        except requests.exceptions.ConnectionError:
            print('ConnectionError')

    filename = Path(args.dest_folder).joinpath(args.json_name)
    create_json(filename, all_books)

    print('DONE!')


if __name__ == '__main__':
    main()
