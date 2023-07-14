#!/bin/sh

echo -e '' > chksum.list

for i in $(find src/articles -type f -name '*.md'); do
    sha224sum $i >> chksum.list
done