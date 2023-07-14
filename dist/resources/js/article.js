let contentFontSize = 18,
    inlineCodeSize = 16,
    blockCodeSize = 14;
let fontFamily = 'CONTENT';

const stylesheetSetter = () => {
    document.styleSheets[0].addRule(':root', `--font-size: ${contentFontSize}px`);
    document.styleSheets[0].addRule(':root', `--code-block-font-size: ${blockCodeSize}px;`);
    document.styleSheets[0].addRule(":root", `--inline-code-font-size: ${inlineCodeSize}px`);
}

document.addEventListener('DOMContentLoaded', () => {
    new Viewer(document.querySelector('main'));
    document.getElementById('backtotop').onclick = e => {
        window.scrollTo({ top: 0 });
    }
    document.getElementById('backtomain').onclick = e => location.assign("/");
    document.getElementById("larger").onclick = () => {
        contentFontSize += 2, inlineCodeSize += 2, blockCodeSize += 2;
        stylesheetSetter();
    }
    document.getElementById("smaller").onclick = () => {
        contentFontSize -= 2, inlineCodeSize -= 2, blockCodeSize -= 2;
        stylesheetSetter();
    }
    document.getElementById("switchfont").onclick = () => {
        document.styleSheets[0].addRule(':root', `--font-family-prose: ${fontFamily === 'CONTENT' ? 'system-ui' : 'CONTENT'}`);
        fontFamily = (fontFamily === 'CONTENT' ? 'system-ui' : 'CONTENT');
    }

    // Non-essential if user has JavaScript off. Just makes checkboxes look nicer.
    const selector = '.task-list > li > input[type="checkbox"]';
    const checkboxes = document.querySelectorAll(selector);
    Array.from(checkboxes).forEach((checkbox) => {
        const wasChecked = checkbox.checked;
        checkbox.disabled = false;
        checkbox.addEventListener('click', (ev) => { ev.target.checked = wasChecked });
    })

    /** Progress bar */
    const winHeight = window.innerHeight,
        docHeight = document.documentElement.scrollHeight,
        progressBar = document.querySelector('#content_progress');
    progressBar.max = docHeight - winHeight;
    progressBar.value = window.scrollY;

    document.addEventListener('scroll', function () {
        progressBar.max = document.documentElement.scrollHeight - window.innerHeight;
        progressBar.value = window.scrollY;
    });
}, false);