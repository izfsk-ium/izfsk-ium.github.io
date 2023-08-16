#!/bin/python3

"""
Read all articles, fetch their metadata
Generate index.html, categories.html, projects.html and rss.xml
"""


import itertools
from os import listdir, path
from pprint import pprint
import re
import string
from urllib.parse import quote_plus
from htmlmin import minify
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
from fontTools import subset
import datetime
import urllib.parse
import yaml
from enum import Enum
from cn2an import an2cn
from itertools import groupby
from json import dump

FINAL_CONTENT = open("src/templates/index.html", "r").read()


class ArticleMetaData:
    def __init__(self, filename: str, data: dict, content: str) -> None:
        self.uuid = data["uuid"]
        self.title = data["title"]
        self.dateStr = str(data["date"])
        self.date = self.get_unix_timestamp(str(data["date"]))
        self.dateObj = datetime.datetime.fromtimestamp(self.date)
        self.category = data["category"]
        self.isOutdated = data.get("outdated", False)
        self.isDraft = data.get("draft", False)

        self.project = data.get("project", None)
        self.htmlPath = (
            "dist/articles/"
            + (
                path.basename(filename)[:-3]
                if data.get("english", None) == None
                else data["english"]
            )
            + ".html"
        )
        self.url = (
            "/articles/"
            + (
                path.basename(filename)[:-3]
                if data.get("english", None) == None
                else data["english"]
            )
            + ".html"
        )
        self.content = content

    def get_unix_timestamp(self, date_string):
        date_obj = datetime.datetime.strptime(date_string, "%Y-%m-%d")
        unix_timestamp = date_obj.timestamp()
        return int(unix_timestamp)

    def __repr__(self) -> str:
        return f"{self.uuid} :: {self.date} :: {self.title} "


def metadata_fetcher():
    """
    Iter src/articles and get metadata of each article
    """
    meta_list = []

    for i in listdir("src/articles"):
        target_file = path.join("src/articles", i)
        assert path.exists(target_file)
        if path.isdir(target_file):
            continue

        # now read metadata
        file_content = open(target_file, "r").read()
        end_index = file_content.find("---", 3)

        if end_index != -1:
            metadata = file_content[3:end_index].strip()

        meta_list.append(
            ArticleMetaData(
                filename=i,
                data=yaml.load(metadata, Loader=yaml.SafeLoader),
                content=file_content,
            )
        )

    return meta_list


def generate_index(articles: list):
    """
    Generate index and recent articles
    """

    def format_unix_timestamp(unix_timestamp):
        date_obj = datetime.datetime.utcfromtimestamp(unix_timestamp)
        formatted_date = date_obj.strftime("%Y-%m-%d")
        return formatted_date

    recent_articles_template = "<ul>\n{ARTICLES}{SUMMARY}</ul>"
    links_html = ""
    for i in list(filter(lambda x: not x.isOutdated and not x.isDraft, articles))[:4]:
        links_html += f"\t<li class='ra'><span>{i.dateObj.strftime('%Y-%m-%d')}</span>&nbsp;&nbsp;<a href='{i.url}'>{i.title}</a></li>\n"

    total_article_count = an2cn(len(articles))
    total_categories_count = an2cn(
        len(
            list(
                groupby(
                    sorted(articles, key=lambda x: x.category), lambda x: x.category
                )
            )
        )
    )
    total_projects_count = an2cn(
        len(
            list(
                groupby(
                    sorted(
                        filter(lambda x: x.project != None, articles),
                        key=lambda x: x.project,
                    ),
                    lambda x: x.project,
                )
            )
        )
    )

    global FINAL_CONTENT
    FINAL_CONTENT = FINAL_CONTENT.replace(
        "<!--%%RECENTLY%%-->",
        recent_articles_template.format(
            ARTICLES=links_html,
            SUMMARY=(
                f'<li>共<a href="/pages/archives.html">{total_article_count}篇</a>，'
                f'归于{total_categories_count}个<a href="/pages/category.html">类别</a>，'
                f'{total_projects_count}个<a href="/pages/projects.html">专题</a>。</li>'
            ),
        ),
    ).replace(
        "<!--%%BUILDTIME%%-->",
        format_unix_timestamp(int(datetime.datetime.now().timestamp())),
    )

    with open("dist/index.html", "w") as fp:
        fp.write(minify(FINAL_CONTENT))
        fp.flush()
        fp.close()

    def get_cjk_and_printable_ascii(text):
        cjk_pattern = re.compile(
            r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]"
        )
        cjk_characters = cjk_pattern.findall(text)

        return "".join(cjk_characters) + string.printable

    # Generate fonts for index.html
    print(" -> Generate CONTENT font for index.html")
    content_characters = "".join(set(get_cjk_and_printable_ascii(FINAL_CONTENT)))
    content_woff2 = [
        "src/resources/fonts/Clear-Hans-Serif.ttf",
        f"--text='{content_characters}'",
        f"--output-file=dist/resources/fonts/ClearHans/ClearHansSerifGB.index.woff2",
        "--flavor=woff2",
        "--with-zopfli",
    ]
    subset.main(content_woff2)

    if path.exists("dist/resources/fonts/FiraCode/FCR.woff2"):
        print(" -X File dist/resources/fonts/FiraCode/FCR.woff2 exists.")
        print("    Mono font for index.html will not generate as it takes much time..")
    else:
        print(" -> Generate MONO font for index.html")
        mono_woff2 = [
            "src/resources/fonts/FiraCode-Regular.ttf",
            f"--text='0123456789'",
            f"--output-file=dist/resources/fonts/FiraCode/FCR.woff2",
            "--flavor=woff2",
            "--with-zopfli",
        ]
        subset.main(mono_woff2)

    if path.exists("dist/resources/fonts/moe.index.woff2"):
        print(" -X File dist/resources/fonts/moe.index.woff2 exists.")
        print("    Title font for index.html will not generate as it takes much time..")
    else:
        sitename_characters = "白漠流霜"
        title_woff2 = [
            "src/resources/fonts/TWSung.ttf",
            f"--text='{sitename_characters}'",
            f"--output-file=dist/resources/fonts/moe.index.woff2",
            "--flavor=woff2",
            "--with-zopfli",
        ]
        subset.main(title_woff2)

    print("Generate index.html done.")


def generate_archive(items: list[ArticleMetaData]):
    MONTH_TABLE: list[str] = [
        "",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    def metaDataToArchiveString(metadata: ArticleMetaData) -> str:
        return f"""
            <div class="archive-entry">
                <h3 class="archive-entry-title">
                    <a href="{metadata.url}">{metadata.title}</a>
                </h3>
                <div class="archive-meta" id="{metadata.uuid}">
                    <span title="{metadata.title}">
                        {metadata.dateObj.strftime("%Y-%m-%d")}
                    </span>&nbsp{metadata.category}
                </div>
            </div>
            """

    class NodeType(Enum):
        YearStart = "YearStart"
        MonthStart = "MonthStart"
        Article = "Article"
        MonthStop = "MonthStop"
        YearStop = "YearStop"

    class Node:
        def __init__(self, raw: ArticleMetaData) -> None:
            self.type = None
            self.data = None
            self.raw = raw

        def __repr__(self) -> str:
            return str(self.type)

        def buildYearStart(self):
            self.type = NodeType.YearStart
            self.data = self.raw.dateObj.year
            return self

        def buildMonthStart(self):
            self.type = NodeType.MonthStart
            self.data = MONTH_TABLE[self.raw.dateObj.month]
            return self

        def buildArticle(self):
            self.type = NodeType.Article
            self.data = self.raw
            return self

        def buildMonthStop(self):
            self.type = NodeType.MonthStop
            return self

        def buildYearStop(self):
            self.type = NodeType.YearStop
            return self

    all_articles: list[ArticleMetaData] = items
    nodeElements: list[Node] = list()

    month_article_counter = {
        x: len(list(y))
        for x, y in itertools.groupby(
            sorted(all_articles, key=lambda x: x.date),
            lambda x: f"{x.dateObj.year}.{x.dateObj.month}",
        )
    }

    ptr_first, ptr_second = itertools.tee(
        iter(sorted(all_articles, key=lambda x: x.date, reverse=True)),
        2,
    )

    # push first year and month to store
    first_element = next(ptr_second)
    string_of_month = MONTH_TABLE[first_element.dateObj.month]
    nodeElements.append(Node(first_element).buildYearStart())
    nodeElements.append(Node(first_element).buildMonthStart())

    # compare two iterator, if have difference, store diff data, catch exceptions
    while True:
        try:
            left = next(ptr_first)
            nodeElements.append(Node(left).buildArticle())
            right = next(ptr_second)
            if left.dateObj.year != right.dateObj.year:
                nodeElements.append(Node(left).buildMonthStop())
                nodeElements.append(Node(left).buildYearStop())
                nodeElements.append(Node(right).buildYearStart())
                nodeElements.append(Node(right).buildMonthStart())
                continue
            if left.dateObj.month != right.dateObj.month:
                nodeElements.append(Node(left).buildMonthStop())
                nodeElements.append(Node(right).buildMonthStart())

        except StopIteration:
            # the left pointers to the last one
            nodeElements.append(Node(first_element).buildMonthStop())
            nodeElements.append(Node(first_element).buildYearStop())
            break

    html_content = "<div>"
    for item in nodeElements:
        match item.type:
            case NodeType.YearStart:
                html_content += f"<li class=l1> {item.data} </li>"
            case NodeType.MonthStart:
                html_content += f"""
                    <div class="archive-month">
                        <h3 class="archive-month-header">
                            {item.data}
                            <sub>{month_article_counter[f'{item.raw.dateObj.year}.{item.raw.dateObj.month}']}</sub>
                        </h3>
                    <div class="archive-posts">
                """
            case NodeType.Article:
                html_content += metaDataToArchiveString(item.raw)
            case NodeType.MonthStop:
                html_content += "</div></div>"
            case NodeType.YearStop:
                html_content += "<br/>"
            case _:
                pass

    def get_cjk_and_english(text):
        cjk_pattern = re.compile(
            r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]+"
        )
        english_pattern = re.compile(r"\b[a-zA-Z]+\b")

        cjk_characters = cjk_pattern.findall(text)
        english_words = english_pattern.findall(text)

        return len(cjk_characters + english_words)

    with open("src/templates/archives.html", "r") as fp_in:
        open("dist/pages/archives.html", "w").write(
            fp_in.read()
            .replace("<!--%%CONTENTS%%-->", minify(html_content))
            .replace(
                "<!--%%SUMMARY%%-->",
                f"<h3>共{an2cn(len(articles))}篇文章，合计 {sum(map(lambda x:(get_cjk_and_english(x.content)),articles))} 字符。</h3>",
            )
        )
        print("Generate archive.html done.")
        fp_in.close()


def generate_category(articles: list[ArticleMetaData]):
    """
    Generate category page
    """
    template = """
    <section><p>共{COUNT}个分类。</p></section>
    <section id="posts">
        {GROUPS}
    </section>
    """
    category_counter = 0
    groups_html = ""

    for key, elems in itertools.groupby(
        sorted(articles, key=lambda x: x.category), lambda x: x.category
    ):
        category_counter = category_counter + 1
        groups_html += f"""
            <h2>{key}</h2>
            <ul>{"&nbsp;".join([f'<li><a href="{x.url}">{x.title}</a></li>' for x in elems])}</ul>
        """

    with open("src/templates/category.html", "r") as fp_in:
        open("dist/pages/category.html", "w").write(
            fp_in.read()
            .replace(
                "<!--%%CONTENTS%%-->",
                minify(
                    template.format(COUNT=an2cn(category_counter), GROUPS=groups_html)
                ),
            )
            .replace(
                "<!--%%BUILDTIME%%-->",
                f"{datetime.datetime.now().strftime('%Y-%m-%d')}",
            )
        )
        print("Generate category.html done.")
        fp_in.close()


def generate_projects(articles: list[ArticleMetaData]):
    """
    Same as generate projects
    """
    template = """
    <section><p>共{COUNT}个专题。</p></section>
    <section id="posts">
        {GROUPS}
    </section>
    """
    project_counter = 0
    groups_html = ""

    for key, elems in itertools.groupby(
        sorted(filter(lambda x: x.project != None, articles), key=lambda x: x.project),
        lambda x: x.project,
    ):
        project_counter = project_counter + 1
        groups_html += f"""
            <h2>{key}</h2>
            <ul>{"&nbsp;".join([f'<li><a href="{x.url}">{x.title}</a></li>' for x in elems])}</ul>
        """

    with open("src/templates/projects.html", "r") as fp_in:
        open("dist/pages/projects.html", "w").write(
            fp_in.read()
            .replace(
                "<!--%%CONTENTS%%-->",
                minify(
                    template.format(COUNT=an2cn(project_counter), GROUPS=groups_html)
                ),
            )
            .replace(
                "<!--%%BUILDTIME%%-->",
                f"{datetime.datetime.now().strftime('%Y-%m-%d')}",
            )
        )
        print("Generate projects.html done.")
        fp_in.close()


def generate_search_json(articles: list[ArticleMetaData]):
    """
    Generate search data for search.
    Schema:
    {"title": string, "content": string, "url": string}
    """

    def remove_markdown_tags(text):
        # Remove Markdown headings (e.g., ## Heading)
        text = re.sub(r"^#+\s", "", text, flags=re.MULTILINE)
        # Remove Markdown emphasis (e.g., *italic*, **bold**)
        text = re.sub(r"(\*{1,2})(.*?)\1", r"\2", text)
        # Remove Markdown links (e.g., [link](https://example.com))
        text = re.sub(r"\[.*?\]\(.*?\)", "", text)
        # Remove Markdown images (e.g., ![alt text](https://example.com/image.jpg))
        text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
        # Remove Markdown code blocks (e.g., ```code```)
        text = re.sub(r"`{3}.*?`{3}", "", text, flags=re.DOTALL)
        # Remove inline code (e.g., `code`)
        text = re.sub(r"`.*?`", "", text)
        # Remove horizontal rules (e.g., ---)
        text = re.sub(r"---+", "", text)
        # Remove remaining Markdown formatting (e.g., **strong**, *emphasis*)
        text = re.sub(r"(\*{1,2})(.*?)\1", r"\2", text)
        return text.strip().replace("\n", " ")

    schema = []
    for i in articles:
        schema.append(
            {"title": i.title, "content": remove_markdown_tags(i.content), "url": i.url}
        )

    dump(schema, open("dist/resources/misc/search.json", "w"), ensure_ascii=False)
    print("Generate search.json Done.")


def generate_rss(articles: list[ArticleMetaData]):
    fg = FeedGenerator()
    fg.id("http://blog.izfsk.top")
    fg.title("白漠流霜")
    fg.author({"name": "izfsk", "email": "me@izfsk.top"})
    fg.link(href="http://blog.izfsk.top", rel="alternate")
    fg.logo("http://blog.izfsk.top/favicon.ico")
    fg.subtitle("Izfsk's blog")
    fg.link(href="http://blog.izfsk.top/rss.xml", rel="self")
    fg.language("zh_CN")

    for i in articles:
        fe = fg.add_entry()
        fe.id(i.uuid)
        fe.title(i.title)
        fe.pubDate(i.dateStr + "T00:00:00+08:00")
        fe.description(i.title)
        fe.content(
            str(BeautifulSoup(open(i.htmlPath, "r").read(), "html.parser").body),
            type="html",
        )
        fe.link(href="https://blog.izfsk.top" + i.url)

    with open("dist/rss.xml", "w") as fp:
        fp.write(fg.rss_str(pretty=True).decode())
        fp.flush()
        fp.close()
        print("Generating rss")


def generate_article_uuid_for_counter(articles: list[ArticleMetaData]):
    dump(
        list(map(lambda x: x.uuid, articles)) + ["index", "test"],
        open("dist/articles/uuids.json", "w"),
    )


def generate_sitemap_xml(articles: list[ArticleMetaData]):
    SITEMAP_XML = """
<?xml version="1.0" encoding="UTF-8"  standalone="yes"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  {STATIC_URLS}
  {BLOGPOST_URLS}
</urlset>
"""
    SITE_ENTRY_TEMPLATE = """
  <url>
    <loc>{URL}</loc>
    <lastmod>{MODIFY}</lastmod>
    <priority>1.00</priority>
  </url>\n"""

    # special sites will never change
    BLOG_URLS = """
  <url>
    <loc>https://blog.izfsk.top/</loc>
    <lastmod>{MODIFY}</lastmod>
    <priority>1.00</priority>
  </url>    
  <url>
    <loc>https://blog.izfsk.top/pages/archives.html</loc>
    <lastmod>{MODIFY}</lastmod>
    <priority>0.60</priority>
  </url>
  <url>
    <loc>https://blog.izfsk.top/pages/category.html</loc>
    <lastmod>{MODIFY}</lastmod>
    <priority>0.60</priority>
  </url>
  <url>
    <loc>https://blog.izfsk.top/pages/projects.html</loc>
    <lastmod>{MODIFY}</lastmod>
    <priority>0.60</priority>
  </url>
  <url>
    <loc>https://blog.izfsk.top/pages/bookmarks.html</loc>
    <lastmod>{MODIFY}</lastmod>
    <priority>0.60</priority>
  </url>
  <url>
    <loc>https://blog.izfsk.top/pages/fs.html</loc>
    <lastmod>{MODIFY}</lastmod>
    <priority>0.60</priority>
  </url>
  <url>
    <loc>https://blog.izfsk.top/pages/books.html</loc>
    <lastmod>{MODIFY}</lastmod>
    <priority>0.60</priority>
  </url>
  <url>
    <loc>https://blog.izfsk.top/pages/movies.html</loc>
    <lastmod>{MODIFY}</lastmod>
    <priority>0.60</priority>
  </url>
  <url>
    <loc>https://blog.izfsk.top/pages/friends.html</loc>
    <lastmod>{MODIFY}</lastmod>
    <priority>0.60</priority>
  </url>
  <url>
    <loc>https://blog.izfsk.top/pages/readme.html</loc>
    <lastmod>{MODIFY}</lastmod>
    <priority>0.60</priority>
  </url>
""".format(
        MODIFY=datetime.datetime.now().isoformat()[0:19] + "+00:00"
    )

    all_blogposts = ""
    for i in articles:
        all_blogposts += SITE_ENTRY_TEMPLATE.format(
            URL=f"https://blog.izfsk.top{urllib.parse.quote(i.url)}",
            MODIFY=i.dateObj.isoformat()[0:19] + "+00:00",
        )
    with open("dist/sitemap.xml", "w") as fp:
        fp.write(SITEMAP_XML.format(STATIC_URLS=BLOG_URLS, BLOGPOST_URLS=all_blogposts))
        fp.flush()
        print("Generating sitemap")


if __name__ == "__main__":
    articles = sorted(metadata_fetcher(), key=lambda x: x.date, reverse=True)
    generate_index(articles)
    generate_archive(articles)
    generate_category(articles)
    generate_projects(articles)
    generate_search_json(articles)
    generate_rss(articles)
    generate_article_uuid_for_counter(articles)
    generate_sitemap_xml(articles)
