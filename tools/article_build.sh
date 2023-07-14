#!/bin/bash

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:./tools

FILE="${1}"

# check if file exists
if [ -z $FILE ];then
    exit 1
fi

if [ -f $FILE ]; then
    :
else 
    echo "$FILE does not exist."
    exit 1
fi


# generate html
basename=${FILE##*/}

echo ">> Processing ${basename}"

pandoc \
  --katex \
  --from markdown+tex_math_single_backslash \
  --to html5+smart \
  --filter ./tools/pandoc-sidenote \
  --template="./src/templates/article.html" \
  --css="/resources/css/article/theme.css" \
  --css="/resources/css/article/code.css" \
  --toc \
  --wrap=none \
  --output "./dist/articles/"${basename%.md}".html" \
  $FILE
