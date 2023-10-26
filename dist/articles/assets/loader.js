function addFontToPage(arrayBuffer, name) {
    const font = new FontFace(name, arrayBuffer);
    document.fonts.add(font);
    font.load().then(e => console.info(name + " : Font loaded."));
}

function fallback(name, location) {
    const elem = document.createElement("style");
    elem.innerHTML = `@font-face {
        font-family: ${name};
        src: url(${location});
        font-display: swap;
    }`;
    document.head.appendChild(elem);
}

function loadFontFull(targets) {
    const IDBRequest = window.indexedDB.open("FONTDB", 1);

    IDBRequest.onerror = e => {
        console.error("Unable to open database.");
        targets.forEach(e => { fallback(e.name, e.location) });
    }
    IDBRequest.onupgradeneeded = function () {
        let db = IDBRequest.result,
            store = db.createObjectStore("Fonts", { keyPath: "id" });
    };

    IDBRequest.onsuccess = function () {
        for (const target of targets) {
            const FONT_CACHE_KEY = `font.${target.name}.downloaded`;

            if (localStorage.getItem(FONT_CACHE_KEY) === null) {
                console.log(target.name + ' : font download start!');

                fetch(target.location)
                    .then(resp => resp.arrayBuffer())
                    .then(arrayBuffer => {
                        console.log('font downloaded successfully!');

                        // Start a new transaction
                        let db = IDBRequest.result,
                            tx = db.transaction("Fonts", "readwrite");
                        let store = tx.objectStore("Fonts");
                        let operation = store.put({
                            id: target.name,
                            data: arrayBuffer
                        });
                        operation.onsuccess = e => {
                            console.log('font stored successfully!');
                            localStorage.setItem(FONT_CACHE_KEY, true);
                            addFontToPage(arrayBuffer, target.name);
                        };
                        operation.onerror = e => {
                            console.error(e);
                            targets.forEach(e => { fallback(e.name, e.location) });
                        }
                    })
                    .catch(e => {
                        console.error(e);
                        targets.forEach(e => { fallback(e.name, e.location) });
                    })
            } else {
                let store = IDBRequest.result.transaction("Fonts", "readwrite").objectStore("Fonts");
                const fontReq = store.get(target.name);
                fontReq.onsuccess = e => {
                    console.log('font loaded from IndexDB successfully!');
                    addFontToPage(fontReq.result.data, target.name);
                };
                fontReq.onerror = e => {
                    console.error(e);
                    targets.forEach(e => { fallback(e.name, e.location) });
                }
            }
        }
    };
}

document.addEventListener("DOMContentLoaded", () => {
    try {
        loadFontFull(FONTS);
    } catch (e) {
        console.error(e);
        FONTS.forEach(e => { fallback(e.name, e.location) });
    }
});