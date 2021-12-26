function arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i]);
    }

    return binary;
}

function show() {
    document.getElementById("show-button").disabled = true;
    let data = {
        args: document.getElementById("json").value,
        code: document.getElementById("code").value
    };

    let json = JSON.stringify(data);

    fetch("/code/", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: json,
    }).then(async res => {
        const contentType = res.headers.get("Content-Type");
        if (contentType === "application/json") {
            await res.json().then(json => {
                toggle_error(json.reason);
            })
        } else if (contentType === "image/png;base64") {
            await res.arrayBuffer().then(buffer => {
                const base64img = arrayBufferToBase64(buffer);
                document.getElementById("code-image").setAttribute("src", "data:image/png;base64," + base64img);
            })
            toggle();
        }
    })

    document.getElementById("show-button").disabled = false;
}

function toggle() {
    // For the image popup
    document.getElementById("popup-1").classList.toggle("active");
}

function toggle_error(error) {
    // For the error popup
    document.getElementById("popup-2").classList.toggle("active");
    document.getElementById("error-msg").innerHTML = error;
}

function dll() {
    let a = document.createElement("a");
    a.href = document.getElementById("code-image").getAttribute("src");
    a.download = "image.png";
    a.click();
}

fetch('/assets/imgs/default-image.json')
    .then(response => response.text())
    .then(text => document.getElementById('json').value = text)
