import requests

from pathlib import Path


def download_book():
    for book_id in range(0, 11):
        url = f'https://tululu.org/txt.php?id={book_id}'

        response = requests.get(url, allow_redirects=False, verify=False)
        response.raise_for_status()

        filename = f'books/{book_id}.txt'
        with open(filename, 'wb') as file:
            file.write(response.content)


def main():
    Path("books").mkdir(parents=True, exist_ok=True)
    download_book()


if __name__ == '__main__':
    main()
