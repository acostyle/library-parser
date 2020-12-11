import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from exceptions import redirect_case


def parse_category(start_page=1, end_page=None):
    book_ids = []

    url = f'https://tululu.org/l55/'

    response = requests.get(f'{url}{start_page}',
                            allow_redirects=False, verify=False)
    response.raise_for_status()
    redirect_case(response)

    if not end_page:
        soup = BeautifulSoup(response.text, 'lxml')
        end_page = int(soup.select('a.npage')[-1].text)

    for page in range(start_page, end_page + 1):

        response = requests.get(
            f'{url}{page}', allow_redirects=False, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        books_cards = [book.select_one('a')['href'][2:]
                       for book in soup.select('div.bookimage')]

        book_ids += books_cards

    return book_ids
