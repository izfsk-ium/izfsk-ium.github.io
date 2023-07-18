let fontFamily = 'CONTENT';

function handleGPGData() {
    function generateUniqueID() {
        const randomString = Math.random().toString(36).substr(2, 9);
        return "encrypted-element" + '-' + randomString;
    }

    function loadScript(url, onLoad, onError) {
        const scriptElement = document.createElement('script');
        scriptElement.src = url;
        scriptElement.onload = function () {
            onLoad();
        };
        scriptElement.onerror = function () {
            onError();
        };
        document.head.appendChild(scriptElement);
    }

    const targetContainers = document.querySelectorAll("pre.gpg");
    const gpgData = {};

    if (targetContainers.length !== 0) {
        for (const i of targetContainers) {
            const newID = generateUniqueID();
            i.setAttribute("id", newID);
            gpgData[newID] = i.innerText;
            i.innerHTML = '<code>Loading GPG Library...</code>';
        }
        loadScript("/resources/js/openpgp.min.js", () => {
            for (const i of targetContainers) {
                i.innerHTML = '';
                // Create the elements programmatically
                const containerDiv = document.createElement('div');
                const spanElement = document.createElement('span');
                spanElement.textContent = 'Input password to decrypt:';
                const inputElement = document.createElement('input');
                inputElement.type = 'password';
                const buttonElement = document.createElement('button');
                buttonElement.textContent = 'OK';

                buttonElement.onclick = async e => {
                    e.preventDefault();
                    if (inputElement.value.length == 0) {
                        alert("No password provided!");
                        return;
                    } else {
                        const message = await openpgp.readMessage({
                            armoredMessage: gpgData[i.getAttribute("id")]
                        });
                        try {
                            const { data: decrypted, signatures } = await openpgp.decrypt({
                                message,
                                passwords: [inputElement.value || ''],
                                format: 'utf8',
                            });
                            const decryptedElement = document.createElement('div');
                            decryptedElement.textContent = decrypted;
                            i.replaceWith(decryptedElement);
                        }
                        catch (e) {
                            alert("密码错误...");
                            console.error(e);
                        }
                    }
                }

                containerDiv.appendChild(spanElement);
                containerDiv.appendChild(document.createElement('br')); // Optional: add a line break
                containerDiv.appendChild(inputElement);
                containerDiv.appendChild(buttonElement);

                i.appendChild(containerDiv);
            }
        }, () => {
            for (const i of targetContainers) {
                i.innerHTML = '<div><code>Failed to load GPG Library</code><div>';
            }
        });
    }

}

document.addEventListener('DOMContentLoaded', () => {
    new Viewer(document.querySelector('main'));
    document.getElementById('backtotop').onclick = e => {
        window.scrollTo({ top: 0 });
    }
    document.getElementById('backtomain').onclick = e => location.assign("/");

    /** remove */
    document.getElementById("larger").style.display = 'none';
    document.getElementById("smaller").style.display = 'none';
    document.getElementById("switchfont").onclick = () => {
        const styleSheet = Array.from(document.styleSheets).find(sheet => sheet.href === null);
        styleSheet.addRule(':root', `--font-family-prose: ${fontFamily === 'CONTENT' ? 'system-ui' : 'CONTENT'}`);
        fontFamily = (fontFamily === 'CONTENT' ? 'system-ui' : 'CONTENT');
    }

    // Non-essential if user has JavaScript off. Just makes checkboxes look nicer.
    const selector = '.task-list > li > input[type="checkbox"]';
    const checkboxes = document.querySelectorAll(selector);
    Array.from(checkboxes).forEach((checkbox) => {
        const c = checkbox.checked;
        checkbox.disabled = false;
        checkbox.addEventListener('click', (ev) => { ev.target.checked = c });
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

    if (document.querySelector(".subtitle").innerHTML == "&nbsp;") {
        document.querySelector(".subtitle").innerHTML = document.querySelector(".date > time:nth-child(1)").innerHTML.substr(5);
    }

    handleGPGData();
}, false);