let loaded = false, mo = null;

const S = e => document.getElementById("search").onclick = e => {
    e.preventDefault();
    if (!loaded) {
        import("/resources/js/search.js").then(m => { m.Search.start(), mo = m; });
        loaded = true;
    } else {
        mo.Search.start();
    }
}

document.addEventListener('DOMContentLoaded', function () {
    S();
});

S();

const target = document.getElementById("counter-span");
const last = localStorage.getItem("lastVisit-index");
const shouldIncrease = last === null || new Date().getTime() - parseInt(last) >= (1000 * 60 * 15);

fetch(shouldIncrease ? "https://counter.izfsk.top/counter/index" : "https://counter.izfsk.top/readOnly/index")
    .then(r => r.text())
    .then(c => {
        if (!c.startsWith("Too"))
            target.innerText = `，本页记载的访问次数是 ${c} 次`;
    })
    .catch(e => console.error(e));


localStorage.setItem("lastVisit-index", new Date().getTime());