import json
import os

from livereload import Server, shell
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked
from pathlib import Path


def get_books_json():
    with open("books.json", "r", encoding="utf8") as json_file:
        books_json = json_file.read()
    return json.loads(books_json)


def on_reload():
    all_books = get_books_json()
    books_per_page = 20

    chunked_books = list(chunked(all_books, books_per_page))

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')
    
    for page, books in enumerate(chunked_books, 1):
        rendered_page = template.render(
            books=books
        )

        with open(f'pages/index{page}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    Path(os.getcwd(), 'pages').mkdir(parents=True, exist_ok=True)

    on_reload()
    server = Server()
    server.watch('*.html', on_reload)
    server.serve(root='')


if __name__ == '__main__':
    main()
