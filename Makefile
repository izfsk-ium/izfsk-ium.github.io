.PHONY:	build

SOURCES := $(shell tools/determine_modified.sh)

test:
	echo "$(SOURCES)"

ideas:
	python3 tools/thoughts.py

bookmarks:
	python3 tools/bookmarks.py

books:
	python3 tools/books.py

fs:
	python3 tools/fs.py

movies:
	python3 tools/movies.py

pages: bookmarks books fs movies ideas

articles_first_pass:
	echo "$(SOURCES)" | xargs -n 1 -P $$(nproc) ./tools/article_build.sh

articles_second_pass: articles_first_pass
	echo "$(SOURCES)" | xargs -n 1 -P $$(nproc) python3 ./tools/article_build.py

articles: articles_first_pass articles_second_pass
	cp src/articles/assets/* dist/articles/assets
	cp src/resources/fs/* dist/fs

hash: articles
	sh tools/genhash.sh

index:
	python3 tools/index_generator.py

# Main build
# - pages : all special pages
# - articles : all articles
# - hash : generate hash
# - index : index page and category, projects
build: pages articles hash index
	python3 tools/graph.py

clean:
	echo '' > chksum.list
	rm dist/articles/*.html
	rm dist/resources/fonts/subsets/*