const html_search = `
    <section>
        <p id="exitSearch">返回</p>
    </section>

    <section>
        <div class="search">
            <label for="search">Search for stuff</label>
            <input id="searchInput" type="search" placeholder="搜索站点内容..." autofocus required />
        </div>
    <section>

    <section>
        <ul id="searchResults">
            <em>正在加载...</em>
        </ul>
    </section>`

let LibraryLoaded = false, SearchContentLoaded = false, searchData = null;
const target = document.getElementById("content");
const originalContent = target.innerHTML;

function Searcher(data, keyWord) {
    function isStringEmptyOrInvisible(text) {
        const regex = /^\s*$/;
        return regex.test(text);
    }
    if (isStringEmptyOrInvisible(keyWord)) {
        return [];
    }
    let results = [];
    for (const i of data) {
        const titleFound = i.title.indexOf(keyWord);
        const contentFound = i.content.indexOf(keyWord)
        if (titleFound !== -1) {
            results.push({
                item: i,
                type: "title",
            });
            continue;
        }
        if (contentFound !== -1) {
            results.push({
                item: i,
                type: "content",
                slice: i.content.substr(contentFound, contentFound + 50) || ""
            });
        }
    }
    return results;
}

export const Search = {
    bindCallback: () => {
        document.getElementById("exitSearch").onclick = e => {
            target.innerHTML = originalContent;
            bindSearchCallBack();
        };
        document.getElementById("searchInput").oninput = e => {
            const resultContainer = document.getElementById("searchResults");
            const keyWord = e.target.value;
            if (!SearchContentLoaded) {
                resultContainer.innerHTML = '<em>正在加载...</em>';
                return;
            }

            /** Now start search */
            const result = Searcher(searchData, keyWord);
            console.log(result);

            /** render them on screen */
            let buffer = "";
            if (result.length === 0) {
                resultContainer.innerHTML = "<em>什么也没有找到</em>";
                return;
            }
            for (const i of result) {
                /** Clip and hightlight */
                if (i.type === "content") {
                    buffer += `
                    <li class="resultCard">
                        <h3><a href=${i.item.url}>${i.item.title}</a></h3>
                        <p>${DOMPurify.sanitize(i.slice)}...</p>
                    </li>`;
                } else {
                    buffer += `
                    <li class="resultCard">
                        <h3 class="highlight">
                            <a href=${i.item.url}>${i.item.title}</a></h3>
                        <p>${DOMPurify.sanitize((i.item.content.substr(0, 25)))}...</p>
                    </li>`;
                }

            }
            resultContainer.innerHTML = buffer;
        }
    },

    start: async () => {
        if (!LibraryLoaded) {
            function loadCSS(url) {
                return new Promise((resolve, reject) => {
                    const link = document.createElement('link');
                    link.rel = 'stylesheet';
                    link.href = url;
                    link.onload = resolve;
                    link.onerror = reject;
                    document.head.appendChild(link);
                });
            }
            await loadCSS("/resources/css/index/search.css");

            function loadScript(url) {
                return new Promise((resolve, reject) => {
                    const script = document.createElement('script');
                    script.src = url;
                    script.onload = resolve;
                    script.onerror = reject;
                    document.head.appendChild(script);
                });
            }
            await loadScript("/resources/js/purify.js")

            LibraryLoaded = true;
        }

        target.innerHTML = html_search;

        const resultContainer = document.getElementById("searchResults");
        if (!SearchContentLoaded) {
            try {
                const req = await fetch("/resources/misc/search.json");
                const data = await req.json();
                searchData = data;
                SearchContentLoaded = true;
                resultContainer.innerHTML = '<em>&nbsp;<em>';
            } catch (e) {
                console.error(e);
                resultContainer.innerHTML = '<em>Failed to fetch search.json</em>'
            } finally {
                document.getElementById("searchInput").value = '';
            }
        } else {
            resultContainer.innerHTML = '<em>&nbsp;<em>';
        }

        Search.bindCallback();
    }
}