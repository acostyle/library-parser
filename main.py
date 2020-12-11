import requests

from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


DOWNLOAD_URL = 'https://tululu.org/txt.php?id='
INFO_URL = 'https://tululu.org/b'


def get_response(book_id):
    response = requests.get(f'{INFO_URL}{book_id}/',
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
    for book_id in range(1, 11):
        book_data = get_response(book_id)

        if book_data.status_code == 302:
            print(f'Книга с ID {book_id} невозможно скачать')
            continue

        title, author = parse_title_and_author(book_data)

        book_name = f'{book_id}. {title}'
        download_books = download_txt(book_id, book_name)
        download_images = download_img(book_data)


if __name__ == '__main__':
    main()