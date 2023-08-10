#!/bin/python3

import htmlmin
import yaml
from datetime import datetime

BOOK_CARD_TEMPLATE = """
<li>{NAME}</li>
"""


def generate_reading():
    watching_html = ""
    finished_html = ""

    for category, items in yaml.load(
        open("./src/data/movies.yaml", "r"), Loader=yaml.loader.SafeLoader
    ).items():
        for movie in items:
            html = BOOK_CARD_TEMPLATE.format(
                NAME=movie["name"],
            )
            if category == "watching":
                watching_html += html
            else:
                finished_html += html

    open("./dist/pages/movies.html", "w").write(
        htmlmin.minify(
            open("./src/templates/movies.html", "r")
            .read()
            .replace("<!--%%NOWWATCHING%%-->", watching_html)
            .replace("<!--%%FINISHED%%-->", (finished_html))
            .replace(
                "<!--%%LASTBUILT%%-->", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
    )


if __name__ == "__main__":
    generate_reading()
    print("Movies : Done.")
