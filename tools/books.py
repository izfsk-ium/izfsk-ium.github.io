#!/bin/python3

import htmlmin
import yaml
from datetime import datetime

BOOK_CARD_TEMPLATE = """
<li><a href="https://www.google.com/search?client=firefox-b-d&q={NAME}+{ISBN}" target=_blank>《{NAME}》</a> by <em>{AUTHOR}</em>
"""


def generate_reading():
    reading_html = ""
    finished_html = ""

    for category, items in yaml.load(
        open("./src/data/books.yaml", "r"), Loader=yaml.loader.SafeLoader
    ).items():
        for book in items:
            html = BOOK_CARD_TEMPLATE.format(
                NAME=book["name"], AUTHOR=book["author"], ISBN=book["isbn"]
            )
            if category == "reading":
                reading_html += html
            else:
                finished_html += html

    open("./dist/pages/books.html", "w").write(
        htmlmin.minify(
            open("./src/templates/books.html", "r")
            .read()
            .replace("<!--%%NOWREADING%%-->", (reading_html))
            .replace("<!--%%FINISHED%%-->", (finished_html))
            .replace(
                "<!--%%LASTBUILD%%-->", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
    )


if __name__ == "__main__":
    generate_reading()
    print("Books : Done.")
