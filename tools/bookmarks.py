#!/bin/python3

import htmlmin
import yaml
from datetime import datetime


def generate():
    CATEGORY_TEMPLATE = """
            <li class="l1">{category}</li>
        """

    HTML_CONTENT = str()

    for category, items in yaml.load(
        open("./src/data/bookmarks.yaml", "r"), Loader=yaml.loader.SafeLoader
    ).items():
        HTML_CONTENT += CATEGORY_TEMPLATE.format(category=category)
        HTML_CONTENT += "\t<ul>"
        for item in items:
            if not item["url"].startswith("http"):
                print("\t Note: this string seems not a valid url...")
            HTML_CONTENT += """
                    <div>
                        <li><a href="{url}" target="_blank">{url}</a></li>
                        <p>{note}</p>
                        <br />
                    </div>
                """.format(
                url=item["url"], note=item["note"]
            )
        HTML_CONTENT += "</ul>"

    open("./dist/pages/bookmarks.html", "w").write(
        htmlmin.minify(
            open("./src/templates/bookmarks.html", "r")
            .read()
            .replace("<!--%%BOOKMARKS%%-->", HTML_CONTENT)
            .replace(
                "<!--%%LASTBUILD%%-->", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
    )


if __name__ == "__main__":
    generate()
    print("Bookmarks : Done.")
