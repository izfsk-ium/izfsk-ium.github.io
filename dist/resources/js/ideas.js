// Copied from https://stream.thesephist.com/

// Tab key in textarea
for (const area of document.querySelectorAll('textarea')) {
    area.addEventListener('keydown', evt => {
        switch (evt.key) {
            case 'Tab': {
                const idx = evt.target.selectionStart;
                if (idx == null) return;
                evt.preventDefault();
                const val = evt.target.value;
                const front = val.substr(0, idx);
                const back = val.substr(idx);
                evt.target.value = front + '\t' + back;
                evt.target.setSelectionRange(idx + 1, idx + 1);
                break;
            }
            case 'Enter': {
                if (!evt.ctrlKey && !evt.metaKey) return;
                evt.preventDefault();
                evt.target.closest('form').submit();
                break;
            }
        }
    });
}

/** Different from original version, we fetch json and render here. */
IdeaList = null;

function render(target) {
    let buffer = '';
    for (const i of target) {
        buffer += `
                <div class="update">
                    <div class="update-t">
                        <a class="clockstamp" id="${i.date}">${i.date}</a>
                    </div>
                    <div class="update-s">
                        ${i.content}
                    </div>
                </div>
            `;
    }
    document.getElementById("feed").innerHTML = buffer;
}

fetch("/resources/misc/thoughts.json")
    .then(r => r.json())
    .then(data => {
        IdeaList = data;
        render(IdeaList);
    })
    .then(() => {
        document.getElementById("searcher").oninput =
            e => render(
                IdeaList.filter(i =>
                    i.content.includes(e.target.value)));
    })