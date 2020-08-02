window.onload = function () {
    addTagElements();
    tagBoxes = document.getElementsByName("tagChecks");
    addFunctionElements();
    dropdown = document.getElementById("functions");

    downloadButton = document.getElementById("downloadButton");
    preview = document.getElementById("preview");
    copyArea = document.getElementById("copyArea");

    classInput = document.getElementById("class");
    classCheck = document.getElementById("enableClass");
    titleInput = document.getElementById("title");
    valueInput = document.getElementById("value");
    pathInput = document.getElementById("path");
    imageInput = document.getElementById("image");
    flagBoxes = document.getElementsByName("flags");
    tagInput = document.getElementById("tags");

    cardImage = document.getElementById("cardImage")

    update();
}

let downloadButton;
let preview;
let copyArea;

let classInput;
let classCheck;
let titleInput;
let valueInput;
let pathInput;
let imageInput;
let flagBoxes;
let tagInput;
let tagBoxes;
let dropdown;

let cardImage;

let filename = "example_card";
let title = "Example Card";
let value = 0;
let imagename = "example_card";
let flags = "set()";
let tags = "set()";
let methods = "";

let url;

function update() {
    pathInput.value = pathInput.value.replaceAll('\\', '/');


    title = titleInput.value || 'Example Card';
    if (!classCheck.checked) {
        classInput.value = titleInput.value.replace(/[^a-zA-Z0-9 ]/g, "").replaceAll(' ', '_').toLowerCase();
    }
    filename = classInput.value || 'example_card';
    value = valueInput.value;

    imagename = imageInput.value;
    if (imagename) {
        imagename = imagename.substr(imagename.lastIndexOf('\\') + 1);
        cardImage.src = "file://" + pathInput.value + "/" + imagename;
        cardImage.style.display = "block";
    } else {
        imagename = filename + '.png';
        cardImage.src = "";
        cardImage.style.display = "none";
    }

    let flagsSet = [];
    for (let i = 0; i < flagBoxes.length; ++i) {
        if (flagBoxes[i].checked) {
            flagsSet.push("CardFlag." + flagBoxes[i].value);
        }
    }
    if (flagsSet.length > 0) {
        flags = "{" + flagsSet.join(", ") + "}";
    } else {
        flags = "set()"
    }

    let tagMatches = tagInput.value.match(/[^\s"]+|"([^"]*)"/g);
    let tagsSet = [];
    if (tagMatches) {
        for (let i = 0; i < tagMatches.length; ++i) {
            if (tagMatches[i].charAt(0) === '"') {
                tagMatches[i] = tagMatches[i].slice(1, -1);
            }
            tagsSet.push('"' + sanitize(tagMatches[i]) + '"');
        }
    }
    for (let i = 0; i < tagBoxes.length; ++i) {
        if (tagBoxes[i].checked) {
            tagsSet.push('"' + tagBoxes[i].value + '"');
        }
    }
    if (tagsSet.length > 0) {
        tags = "{" + tagsSet.join(", ") + "}";
    } else {
        tags = "set()"
    }

    let py = get_formatted();
    preview.innerHTML = py;
    hljs.highlightBlock(preview);
    let data = new Blob([py], {type: 'text/plain'});
    if (url) {
        window.URL.revokeObjectURL(url);
    }
    url = window.URL.createObjectURL(data);
    downloadButton.download = filename + ".py";
    downloadButton.href = url;
}

function classUpdate() {
    classInput.disabled = !classCheck.checked;
    update();
}

function addFunction() {
    methods += dropdown.value;
    update();
}

function clearFunctions() {
    methods = "";
    update();
}

function reset() {
    classInput.value = "";
    titleInput.value = "";
    valueInput.value = 0;
    imageInput.value = "";
    for (let i = 0; i < flagBoxes.length; ++i) {
        flagBoxes[i].checked = false;
    }
    tagInput.value = "";

    update();
}

function copy() {
    copyArea.value = get_formatted();
    copyArea.select();
    document.execCommand("copy");
}

function get_formatted() {
    return `from objects import Card${flags === "set()" ? "" : ", CardFlag"}


class ${filename}(Card):
    def init(self):
        self.val = ${value}
        self.name = '${sanitize(title)}'
        self.image = '${imagename}'
        self.flags = ${flags}
        self.tags = ${tags}
${methods}`;
}

function sanitize(s) {
    return s.replace(/(?=['"\\])/g, '\\')
}
