#!/bin/python3

from typing import List, Dict, Union, Generator
import yaml
import itertools
from pprint import pprint
from os import path, listdir
from urllib.parse import urlparse
import hashlib


"""
Generate graph data for vis.js

Input :
    all yaml files in src/data/graph

Output:
    - dist/resources/js/grapg.js
"""


def hash_string_to_number(string):
    hashed = hashlib.md5(string.encode()).hexdigest()[0:8]
    number = int(hashed, 16)  # Convert hexadecimal hash to integer
    return number


def get_hostname(url):
    parsed_url = urlparse(url)
    return parsed_url.hostname


class FileInfo:
    def __init__(self, data, filename: str) -> None:
        self.site: Site
        self.edges: List[Site] = []

        print(">> Process " + filename)

        for i in data:
            if i["site"] == "self":
                name = (
                    get_hostname(filename) if filename.startswith("http") else filename
                )

                id = hash_string_to_number(name)
                print(f"ME   {id} " + name)
                self.site = Site(id, name, i["icon"], i["site"])
                continue
            else:
                name = get_hostname(i["site"])

                id = hash_string_to_number(name)
                print(f"EDGE {id} " + name)
                self.edges.append(Site(id, name, i["icon"], i["site"]))

    def __repr__(self) -> str:
        return f"{self.site.id} :: {self.site.name} :: [{self.edges.__len__()}]"


class Site:
    def __init__(self, id, name, icon, site) -> None:
        self.id: int = id
        self.name: str = name
        self.icon: str = icon
        self.site: str = site

    def node_info(self) -> str:
        return f"""
        {{
            id: {self.id},
            label: "{self.name}",
            group: "{0}",
            image: "{self.icon}",
            shape: "image",
        }},
        """


def load_data():
    """
    Load data from disk
    """
    for i in listdir("src/data/graph"):
        data = yaml.load(
            open(path.join("src/data/graph", i), "r"), Loader=yaml.loader.SafeLoader
        )
        yield FileInfo(data=data, filename=i[:-5])


if __name__ == "__main__":
    all_files = list(load_data())
    all_sites = []

    nodes = "var nodes = [ \n"
    edges = "var edges = [ \n"

    for site in all_files:
        nodes += site.site.node_info()
        all_sites.append(site.site)

        for i in site.edges:
            if i.id not in [x.id for x in all_sites] and i.icon != "":
                all_sites.append(i)
                nodes += i.node_info()
            edges += f"\t{{ from: {site.site.id}, to: {i.id} }},\n"

    with open("dist/resources/js/graph.js", "w") as fp:
        fp.write(nodes + "];" + edges + "];")
        fp.flush()
        fp.close()
        print("Generate Graph.js Done.")
