import json

from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape


with open("books.json", "r", encoding='utf-8') as my_file:
    all_books = my_file.read()


env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.html')

with open("books.json", "r") as json_file:
    books_json = json_file.read()

books = json.loads(books_json)

rendered_page = template.render(
    books=books
)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)

server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
server.serve_forever()
