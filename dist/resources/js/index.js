let loaded = false, mo = null;

const bscb = e => document.getElementById("search").onclick = e => {
    e.preventDefault();
    if (!loaded) {
        import("/resources/js/search.js").then(m => { m.Search.start(), mo = m; });
        loaded = true;
    } else {
        mo.Search.start();
    }
}

document.addEventListener('DOMContentLoaded', function () {
    bscb();
});

bscb();

// load counter 
const target = document.getElementById("counter-span");
fetch("https://counter.izfsk.top/counter/index")
    .then(r => r.text())
    .then(c => {
        if (!c.startsWith("Too"))
            target.innerText = `，本页面的访问量是 ${c} 次`;
    })
    .catch(e => console.error(e));