#!/bin/python3

# from os import getcwd, listdir, path
# from datetime import datetime
# from json import dump
# import htmlmin


# def process_file(filename: str):
#     ctime = path.getctime(filename)
#     data = open(filename, "r").read()
#     date = datetime.utcfromtimestamp(ctime).strftime("%y-%m-%d %H:%M")

#     return {
#         "date": date,
#         "title": path.basename(filename).strip(".html"),
#         "content": htmlmin.minify(data),
#     }


# if __name__ == "__main__":
#     ideas = []
#     for i in listdir("./src/data/thoughts"):
#         target = process_file("./src/data/thoughts/" + i)
#         ideas.append(target)

#     with open("dist/resources/misc/thoughts.json", "w") as fp:
#         dump(ideas, fp, ensure_ascii=False)
#         fp.flush()
#         fp.close()
#     print("Thoughts : Done.")

print("Thougths is no longer avilable.")
