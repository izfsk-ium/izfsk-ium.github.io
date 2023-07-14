let loaded = false, mo = null;

const bindSearchCallBack = e => document.getElementById("search").onclick = e => {
    e.preventDefault();
    if (!loaded) {
        import("/resources/js/search.js").then(m => { m.Search.start(), mo = m; });
        loaded = true;
    } else {
        mo.Search.start();
    }
}

document.addEventListener('DOMContentLoaded', function () {
    bindSearchCallBack();
});

bindSearchCallBack();
