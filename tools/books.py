#!/bin/python3

import htmlmin
import yaml
from datetime import datetime

BOOK_CARD_TEMPLATE = """
 <div class="col" ontouchstart="this.classList.toggle('hover');">
    <div class="container" onclick="window.open('https://www.google.com/search?q={ISBN}')">
        <div class="front" style="background-image: url({COVER})">
            <div class="inner" >
                <p class="name">{NAME}</p>
                <span class="author">{AUTHOR}</span>
            </div>
        </div>
        <div class="back">
            <div class="inner">
                <p>{DETAIL}</p>
            </div>
        </div>
    </div>
</div>
"""


def generate_reading():
    reading_html = ""
    finished_html = ""

    for category, items in yaml.load(
        open("./src/data/books.yaml", "r"), Loader=yaml.loader.SafeLoader
    ).items():
        for book in items:
            html = BOOK_CARD_TEMPLATE.format(
                COVER=book["cover"],
                NAME=book["name"],
                ISBN=book["isbn"],
                AUTHOR=book["author"],
                DETAIL=book["description"],
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
