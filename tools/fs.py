#!/bin/python3


from datetime import datetime
from htmlmin import minify
from magic import from_file
from hashlib import sha224
from os.path import getsize, getmtime
from os import listdir

FILE_ITEM_TEMPLATE = """
<tr>
    <td class="filename">
        <a href="{LINK}" download="{NAME}">{NAME}</a>
    </td>
    <td>
        {SIZE}
    </td>
    <td>
        {TIME}
    </td>
    <td>
        {TYPE}
    </td>
    <td class="sha">
        {SHA224}
    </td>
</tr>
"""


def get_size_in_good_formate(file_path, isFile=True):
    if isFile:
        value = getsize(file_path)
    else:
        value = file_path
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size


def generate_file_page():
    buff_files_html = ""
    total_file_size, total_file_count = 0, 0
    for file in listdir("./src/resources/fs"):
        file_path = "./src/resources/fs/" + file
        total_file_count += 1
        total_file_size += getsize(file_path)
        hash = sha224()
        with open(file_path, "rb") as fp:
            for buff in iter(lambda: fp.read(8192), b""):
                hash.update(buff)

        buff_files_html += FILE_ITEM_TEMPLATE.format(
            LINK="/fs/{name}".format(name=file),
            NAME=file,
            SIZE=get_size_in_good_formate(file_path),
            TIME=datetime.fromtimestamp(getmtime(file_path)).__str__()[:19],
            TYPE=from_file(file_path, mime=True),
            SHA224=hash.hexdigest(),
        )

    open("./dist/pages/fs.html", "w").write(
        minify(
            open("./src/templates/fs.html")
            .read()
            .replace("<!--%%FS%%-->", buff_files_html)
            .replace(
                "<!--%%LASTBUILD%%-->", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            .replace(
                "<!--%%SUMMARY%%-->",
                "<br/>\nTotal {size}, {count} files.".format(
                    size=get_size_in_good_formate(total_file_size, isFile=False),
                    count=total_file_count,
                ),
            )
        )
    )


if __name__ == "__main__":
    generate_file_page()
    print("FS : Done.")
