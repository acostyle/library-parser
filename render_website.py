import json

from livereload import Server, shell
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked


def get_books_json():
    with open("books.json", "r") as json_file:
        books_json = json_file.read()

        return json.loads(books_json)


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    books = get_books_json()
    books_per_page = 20

    chunked_books = chunked(books, books_per_page)

    rendered_page = template.render(
        chunked_books=chunked_books
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='')


if __name__ == '__main__':
    main()
