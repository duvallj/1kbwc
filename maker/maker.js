window.onload = function(){
	update();
}

let downloadButton = document.getElementById("downloadButton");
let preview = document.getElementById("preview");
let copyArea = document.getElementById("copyArea");

let classInput = document.getElementById("class");
let classCheck = document.getElementById("enableClass");
let titleInput = document.getElementById("title");
let valueInput = document.getElementById("value");
let pathInput = document.getElementById("path");
let imageInput = document.getElementById("image");
let flagBoxes = document.getElementsByName("flags");

let cardImage = document.getElementById("cardImage");

let filename = "example_card";
let title = "Example Card";
let value = 0;
let imagename = "example_card";
let flags = "set()";
let handlers = "";

let url;

function update(){
	pathInput.value = pathInput.value.replaceAll('\\', '/');
	
	
	title = titleInput.value || 'Example Card';
	if(!classCheck.checked){
		classInput.value = titleInput.value.replace(/[^a-zA-Z0-9 ]/g, "").replaceAll(' ', '_').toLowerCase();
	}
	filename = classInput.value || 'example_card';
	value = valueInput.value;
	
	imagename = imageInput.value;
	if(imagename){
		imagename = imagename.substr(imagename.lastIndexOf('\\') + 1);
		cardImage.src = "file://" + pathInput.value + "/" + imagename;
		cardImage.style.display = "block";
	}else{
		imagename = filename + '.png';
		cardImage.src = "";
		cardImage.style.display = "none";
	}
	
	let flagsSet = [];
	for(let i = 0; i < flagBoxes.length; ++i){
		if(flagBoxes[i].checked){
			flagsSet.push("CardArea." + flagBoxes[i].value);
		}
	}
	if(flagsSet.length > 0){
		flags = "{" + flagsSet.join(", ") + "}";
	}else{
		flags = "set()"
	}
	
	let py = get_formatted();
	preview.innerHTML = py;
	hljs.highlightBlock(preview);
	let data = new Blob([py], {type: 'text/plain'});
	if(url){
		window.URL.revokeObjectURL(url);
	}
	url = window.URL.createObjectURL(data);
	downloadButton.download = filename + ".py";
	downloadButton.href = url;
}

function classUpdate(){
	classInput.disabled = !classCheck.checked;
	update();
}

function reset(){
	classInput.value = "";
	titleInput.value = "";
	valueInput.value = 0;
	imageInput.value = "";
	for(let i = 0; i < flagBoxes.length; ++i){
		flagBoxes[i].checked = false;
	}
	
	update();
}

function copy(){
	copyArea.value = get_formatted();
	copyArea.select();
	document.execCommand("copy");
}

function get_formatted(){
	return `from objects import Card


class ${filename}(Card):
    def init(self):
        self.val = ${value}
        self.name = '${title}'
        self.image = '${imagename}'
        self.flags = ${flags}
${handlers}`;
}