#!/bin/python3

# the second pass of building article
import hashlib
import re
from sys import argv
from fontTools import subset
import os
import string
from datetime import datetime
import yaml


SRC_FILE = argv[1]
HTML_FILE = (
    os.path.splitext(os.path.join("dist/articles", os.path.basename(SRC_FILE)))[0]
    + ".html"
)

assert os.path.exists(SRC_FILE)
assert os.path.exists(HTML_FILE)

MARKDOWN_CONTENT = open(SRC_FILE, "r").read()
TARGET_UUID = ""
RAW_CONTENT = open(HTML_FILE, "r").read()

CSS_TEMPLATE = """
<style>
@font-face {{
  font-family: CONTENT;
  src: url('{WOFF2PATH}') format('woff2'),
       url('{TTFPATH}') format('truetype');
}}
</style>
"""


def font_minify():
    """
    Use fonttools to minify fonts, save them in resources/fonts/subsets
    name of new fonts : 'FT'+uuid
    types of new fonts : ttf woff2
    insert CSS imports in article (replace <!--%%FONTS%%--> )
    """
    global RAW_CONTENT
    font_filename = "FT" + TARGET_UUID
    font_filepath = os.path.join("dist/resources/fonts/subsets/", font_filename)
    font_distpath = os.path.join("/resources/fonts/subsets/", font_filename)

    chinese_characters = ""
    for n in re.findall(r"[\u4e00-\u9fff]+", RAW_CONTENT):
        chinese_characters += n
    target_characters = (
        "".join(set(chinese_characters))
        + "。，、；：「」『』！？《》〈〉“”‘’1234567890"
        + string.printable
    )

    generate_woff2 = [
        "src/resources/fonts/Clear-Hans-Serif.ttf",
        f"--text='{target_characters}'",
        f"--output-file={font_filepath}.woff2",
        "--flavor=woff2",
        "--with-zopfli",
    ]

    generate_ttf = [
        "src/resources/fonts/Clear-Hans-Serif.ttf",
        f"--text='{target_characters}'",
        f"--output-file={font_filepath}.ttf",
    ]

    subset.main(generate_ttf)
    subset.main(generate_woff2)

    RAW_CONTENT = RAW_CONTENT.replace(
        "<!--%%FONTS%%-->",
        CSS_TEMPLATE.format(
            WOFF2PATH=font_distpath + ".woff2", TTFPATH=font_distpath + ".ttf"
        ),
    )


def save_buildtime():
    """
    replace <!--%%BUILDTIME%%--> as build time
    """
    global RAW_CONTENT
    RAW_CONTENT = RAW_CONTENT.replace(
        "<!--%%BUILDTIME%%-->", datetime.now().strftime("%Y-%m-%d")
    )


def save_reflinks():
    """
    Save ref links in markdown
    """
    global TARGET_UUID
    global RAW_CONTENT

    ref_template = """
    <h2>参考链接</h2>
    <ul id="reference">
      {REFS}
    </ul>
    """
    end_index = MARKDOWN_CONTENT.find("---", 3)  # 从索引3开始搜索，避免匹配到第一行的 "---"

    if end_index != -1:
        metadata = MARKDOWN_CONTENT[3:end_index].strip()
    data = yaml.load(metadata, Loader=yaml.SafeLoader)
    TARGET_UUID = data["uuid"]

    try:
        RAW_CONTENT = RAW_CONTENT.replace(
            "<!--%%REF%%-->",
            ref_template.format(
                REFS="\n".join(
                    [
                        f'<li><strong>{i["name"]}</strong>：<a href="{i["url"]}" target="_blank">{i["url"]}</a></li>'
                        for i in data["ref"]
                    ]
                )
            ),
        )
    except KeyError:
        pass


if __name__ == "__main__":
    save_buildtime()
    save_reflinks()
    font_minify()

    with open(HTML_FILE, "w") as fp:
        fp.write(RAW_CONTENT)
        fp.flush()
        fp.close()
    print(f"{TARGET_UUID} :: Pass 2 Done.")
