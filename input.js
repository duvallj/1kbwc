function sendCommand(){
	let input = document.getElementById("input");
	let output = document.getElementById("output");
	console.log(input.value);
	if(input.value){
		addToOutput(input.value);
		let tokens = input.value.split(/[ ,]+/);
		let command = tokens[0];
		let args = tokens.slice(1);
		console.log(command);
		console.log(args);
		input.value = "";
	}
}

function addToOutput(s){
	let output = document.getElementById("output");
	output.innerHTML += "\n" + s;
	output.scrollTop = output.scrollHeight;
}

window.onload = function(){
	let input = document.getElementById("input");
	input.addEventListener("keyup", function(event){
		if(event.keyCode === 13){
			event.preventDefault();
			document.getElementById("submit").click();
		}
	});
}