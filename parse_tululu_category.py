import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from exceptions import raise_if_redirect


def request_book_page(page, url):

    response = requests.get(url, allow_redirects=False, verify=False)
    raise_if_redirect(response)
    response.raise_for_status()

    return response.text


def parse_books_urls(book_page, book_url):
    book_urls = []
    soup = BeautifulSoup(book_page, 'lxml')
    blocks_html = soup.select('table.d_book')

    for block_html in blocks_html:
        url = block_html.select_one('a')['href']
        book_urls.append(urljoin(book_url, url))

    return book_urls


def parse_category(start_page=1, end_page=None):
    book_urls = []

    if not end_page:
        soup = BeautifulSoup(response.text, 'lxml')
        end_page = int(soup.select('a.npage:last-of-type').text)

    for page in range(start_page, end_page + 1):
        url = f'https://tululu.org/l55/{page}'

        book_page = request_book_page(page, url)
        book_urls += parse_books_urls(book_page, url)

    return book_urls
