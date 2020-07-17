window.onload = function(){
	addTagElements();
	tagBoxes = document.getElementsByName("tagChecks");
	addFunctionElements();
	dropdown = document.getElementById("functions");
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
let tagInput = document.getElementById("tags");
let tagBoxes;
let dropdown;

let cardImage = document.getElementById("cardImage");

let filename = "example_card";
let title = "Example Card";
let value = 0;
let imagename = "example_card";
let flags = "set()";
let tags = "set()";
let methods = "";

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
			flagsSet.push("CardFlag." + flagBoxes[i].value);
		}
	}
	if(flagsSet.length > 0){
		flags = "{" + flagsSet.join(", ") + "}";
	}else{
		flags = "set()"
	}
	
	let tagMatches = tagInput.value.match(/[^\s"']+|"([^"]*)"|'([^']*)'/g);
	let tagsSet = [];
	if(tagMatches){
		for(let i = 0; i < tagMatches.length; ++i){
			if(tagMatches[i].charAt(0) === '"'){
				tagsSet.push(tagMatches[i]);
			}else{
				tagsSet.push('"' + tagMatches[i] + '"');
			}
		}
	}
	for(let i = 0; i < tagBoxes.length; ++i){
		if(tagBoxes[i].checked){
			tagsSet.push('"' + tagBoxes[i].value + '"');
		}
	}
	if(tagsSet.length > 0){
		tags = "{" + tagsSet.join(", ") + "}";
	}else{
		tags = "set()"
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

function addFunction(){
	methods += dropdown.value;
	update();
}

function clearFunctions(){
	methods = "";
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
	tagInput.value = "";
	
	update();
}

function copy(){
	copyArea.value = get_formatted();
	copyArea.select();
	document.execCommand("copy");
}

function get_formatted(){
	return `from objects import Card${flags === "set()" ? "" : ", CardFlag"}


class ${filename}(Card):
    def init(self):
        self.val = ${value}
        self.name = '${title}'
        self.image = '${imagename}'
        self.flags = ${flags}
        self.tags = ${tags}
${methods}`;
}
