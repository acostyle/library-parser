import requests
import json

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


def download_txt(book_id, filename, folder='books/'):
    Path(folder).mkdir(parents=True, exist_ok=True)

    url = f'{DOWNLOAD_URL}{book_id}'

    response = requests.get(url, allow_redirects=False, verify=False)
    response.raise_for_status()

    path_to_save = Path(folder).joinpath(f'{filename}.txt')

    with open(path_to_save, 'wb') as file:
        file.write(response.content)

    return str(path_to_save)


def download_img(book_data, folder='images/'):
    Path(folder).mkdir(parents=True, exist_ok=True)

    image_url = parse_img(book_data)

    response = requests.get(image_url, allow_redirects=False, verify=False)
    response.raise_for_status()

    filename = sanitize_filename(image_url.split('/')[-1])

    path_to_save = Path(folder).joinpath(f'{filename}')

    with open(path_to_save, 'wb') as image:
        image.write(response.content)

    return str(path_to_save)


def download_book():
    books = []
    book_ids = parse_category()

    for book_id in book_ids:
        book_data = get_book_info(INFO_URL, book_id)

        title, author = parse_title_and_author(book_data)

        book = {
            'title': title,
            'author': author,
            'img_path': download_img(book_data),
            'book_path': download_txt(book_id, title),
            'comments': parse_comments(book_data),
            'genre': parse_genres(book_data)
        }

        books.append(book)

    return books


def create_json(filename, obj):
    with open(filename, 'w') as file:
        json.dump(obj, file, ensure_ascii=False).encode('utf8')


def parse_genres(book_data):
    soup = BeautifulSoup(book_data.text, 'lxml')
    genres = [genre.find('a').text for genre in soup.find_all(
        'span', class_='d_book')]

    return genres


def parse_comments(book_data):
    soup = BeautifulSoup(book_data.text, 'lxml')
    comments = [comment.find(
        'span', class_='black').text for comment in soup.find_all('div', class_='texts')]

    return comments


def parse_img(book_data):
    soup = BeautifulSoup(book_data.text, 'lxml')
    image_link = soup.find('div', class_='bookimage').find('img')['src']

    return urljoin(INFO_URL, image_link)


def parse_title_and_author(book_data):
    soup = BeautifulSoup(book_data.text, 'lxml')

    title_and_author = soup.find('h1').text.split('\xa0 :: \xa0')

    title = title_and_author[0].strip()
    author = title_and_author[1].strip()

    return sanitize_filename(title), sanitize_filename(author)


def main():
    books = download_book()
    create_json('books.json', books)


if __name__ == '__main__':
    main()
