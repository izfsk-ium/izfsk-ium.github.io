#!/bin/sh

# determine files that need process

sum=0

for FILE in $(find src/articles -type f -name '*.md');do
    old_hash=$(grep -iR $FILE ./chksum.list | awk '{print $1}')
    new_hash=$(sha224sum $FILE | awk '{print $1}')

    if [[ $old_hash == $new_hash ]]; then
       :
    else
        let "sum+=1"
        echo -n "$FILE "
    fi
done

if [ $sum -eq 0 ];then 
    echo -n "没有文章修改，放弃。"
    exit 1
fi