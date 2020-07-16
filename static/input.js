let choices = [];  // Options for the choice state, empty indicates non-choice state
let playerName = "nonexistent";

let commandHistory = [];
let historyIndex = -1;
let historyBuffer = "";

/// Process the input field when the button is clicked.
function on_submit(){
	let v = input.value;
	console.log(v);
	if(v){
		let r = {
			data: "",
			send: false,
			output: "none",
			clear: true
		};
		if(choices.length === 0){
			r = parse(r, tokenize(v));
		}else{  // Choice mode
			r = choiceParse(r, tokenize(v));
		}
		if(r.output === "input"){
			add_to_output(">>> " + v);
		}
		if(r.output === "fail"){
			add_to_output("%%% Failed to parse: " + v);
		}
		if(r.output === "data"){
			add_to_output("%%% " + r.data);
		}
		if(r.send){
			send_on_websocket(JSON.stringify(r.data));
		}
		if(r.clear){
			input.value = "";
			commandHistory.unshift(v);
			historyIndex = -1;
			historyBuffer = "";
		}
	}
}

const HELPSTRINGS = {
	"help": {
		"usage": "help [command]",
		"details": "Display the available commands, or help on specific commands."
	},
	"draw": {
		"usage": "draw",
		"details": "Draw a single card from the deck to your hand."
	},
	"play": {
		"usage": "play index dst",
		"details": "Play the card at `index` in your hand to `dst`."
	},
	"end": {
		"usage": "end [comment]",
		"details": "End your turn."
	},
	"inspect": {
		"usage": "inspect area index",
		"details": "Display the card in `area` at `index` in the inspect window."
	},
	"discard": {
		"usage": "discard area index",
		"details": "Discard the card in `area` at `index`."
	},
	"move": {
		"usage": "move src index dst",
		"details": "Move the card in `src` at `index` to `dst`."
	}
}
const NOTENOUGHARGS = "Not enough arguments: ";

function tokenize(v){
	let matches = v.match(/[^\s"']+|"([^"]*)"|'([^']*)'/g);
	let tokens = [];
	for(let i = 0; i < matches.length; ++i){
		console.log(i.toString() + " " + matches[i]);
		if(matches[i].charAt(0) === '"'){
			if(matches[i].length >= 3){
				tokens.push(matches[i].slice(1, -1));
			}else{
				console.log("Invalid token: " + matches[i]);
				return false;
			}
		}else{
			tokens.push(matches[i]);
		}
	}
	return tokens;
}

function parse(r, tokens){
	if(tokens.length < 1){
		r.output = "fail";
		return r;
	}
	
	let command = tokens[0];
	let args = tokens.slice(1);
	console.log("tokens: " + tokens);
	console.log("command: " + command);
	console.log("args: " + args);
	
	switch(command.toLowerCase()){
		case "help":
		case "h":
			return help(r, args);
			break;
		case "draw":
		case "d":
			return draw(r, args);
			break;
		case "play":
		case "p":
			return play(r, args);
			break;
		case "end":
		case "e":
			return end(r, args);
			break;
		case "inspect":
		case "i":
			return readInspect(r, args);
			break;
		case "discard":
			return discard(r, args);
			break;
		case "move":
		case "m":
			return readMove(r, args);
			break;
		default:
			r.output = "fail";
			return r;
	}
	console.log("what.");
}

function choiceParse(r, tokens){
	if(tokens.length < 1){
		r.output = "fail";
		return r;
	}
	
	let command = tokens[0];
	let num = parseInt(command);
	
	if(!isNaN(num)){  // Choiche
		if(num < 1 || num > choices.length){
			r.output = "data";
			r.data = "Index " + num.toString() + " is out of range.";
			return r;
		}
		// validdd
		r.send = true;
		r.output = "input";
		r.data = {
			"cmd": "choose",
			"which": num,
			"caller": playerName
		}
		choices = [];
		return r;
	}
	
	switch(command){
		case "inspect":
		case "i":
			return readInspect(r, args);
			break;
		case "again":
		case "a":
			r.output = "data";
			r.data = formatChoices(choices);
			return r;
		default:
			r.output = "fail";
			return r;
	}
	console.log("what,");
}

function formatChoices(c){
	s = "Options:";
	for(let i = 0; i < c.length; ++i){
		s += `\n<span class="index"> [${i+1}]</span> <span class="choiceOption">${c[i]}</span>`;
	}
	return s;
}

/// Parse and send a help command.
function help(r, args){
	if(args.length === 0){
		r.data = "Commands available:"
		let cmds = Object.keys(HELPSTRINGS);
		for(let i = 0; i < cmds.length; ++i){
			r.data += "\n - " + HELPSTRINGS[cmds[i]].usage;
		}
		r.output = "data";
	}else{  // fixme: do something else if no commands are valid.
		let first = true;
		for(let i = 0; i < args.length; ++i){
			if(HELPSTRINGS[args[i]]){
				if(first){
					first = false;
				}else{
					r.data += "\n";
				}
				r.data += HELPSTRINGS[args[i]].usage + "\n - " + HELPSTRINGS[args[i]].details;
			}
		}
		r.output = "data";
	}
	return r;
}

/// Parse and send a draw command.
function draw(r, args){
	if(args.length === 0){
		args = ["drawpile", 1, playerName + ".hand"];
		return move(r, args);
	}
	r.output = "fail";
	return r;
}

/// Parse and send a play command.
function play(r, args){
	if(args.length === 2){
		args.unshift(playerName + ".hand");
		if(args[2].indexOf('.') === -1){  // Might be a player name
			if(document.getElementById("play-state").innerHTML.indexOf("<span class=\"playerName\">" + args[2] + "</span>") !== -1){
				// There exists a player with the name in args[2]
				args[2] += ".play";
				console.log("modified play target to " + args[2]);
			}
		}
		return move(r, args);
	}
	if(args.length < 2){
		r.data = NOTENOUGHARGS + HELPSTRINGS.play.usage;
		r.output = "data";
		r.clear = false;
		return r;
	}
	r.output = "fail";
	return r;
}

/// Parse and send an end turn request.
function end(r, args){
	r.send = true;
	r.output = "input";
	r.data = {
		"cmd": "end",
		"caller": playerName,
		"comment": ""
	};
	if(args.length > 0){
		r.data.comment = args.join(" ");
	}
	return r;
}

function readInspect(r, args){
	if(args.length === 2){
		if(args[0] === "hand"){
			args[0] = playerName + ".hand";
		}
		return inspect(r, args);
	}
	if(args.length < 2){
		r.data = NOTENOUGHARGS + HELPSTRINGS.inspect.usage;
		r.output = "data";
		r.clear = false;
		return r;
	}
	r.output = "fail";
	return r;
}

/// Parse and send an inspect command.
function inspect(r, args){
	let area = args[0];
	let index = parseInt(args[1], 10);
	
	if(isNaN(index) || index < 0){
		console.log("Bad index");
		r.output = "fail";
		return r;
	}
	
	r.send = true;
	r.output = "input";
	r.data = {
		"cmd": "inspect",
		"caller": playerName,
		"area": area,
		"index": index
	};
	return r;
}

function discard(r, args){
	if(args.length === 2){
		args.push("discard");
		return move(r, args);
	}
	if(args.length < 2){
		r.data = NOTENOUGHARGS + HELPSTRINGS.discard.usage;
		r.output = "data";
		r.clear = false;
		return r;
	}
	r.output = "fail";
	return r;
}

function readMove(r, args){
	if(args.length === 3){
		return move(r, args);
	}
	if(args.length < 3){
		r.data = NOTENOUGHARGS + HELPSTRINGS.move.usage;
		r.output = "data";
		r.clear = false;
		return r;
	}
	r.output = "fail";
	return r;
}

/// Parse and send a move.
function move(r, args){
	let src = args[0];
	let index = parseInt(args[1], 10);
	let dst = args[2];
	
	if(isNaN(index) || index < 0){
		console.log("Bad index");
		r.output = "fail";
		return r;
	}
	
	r.send = true;
	r.output = "input";
	r.data = {
		"cmd": "move",
		"caller": playerName,
		"src": src,
		"index": index,
		"dst": dst
	};
	return r;
}

/// Set the buffer to the proper value in the history, since something just changed.
function historyUpdate(){
	input.value = historyIndex >= 0 ? commandHistory[historyIndex] : historyBuffer;
}

/// Send command on enter.
window.onload = function(){
	input.addEventListener("keyup", function(event){
		switch(event.keyCode){
			case 13:  // Enter
				event.preventDefault();
				document.getElementById("submit").click();
				break;
		}
	});
	input.addEventListener("keydown", function(event){
		switch(event.keyCode){
			case 38:  // Up 
				event.preventDefault();
				historyIndex = Math.min(historyIndex + 1, commandHistory.length - 1);
				historyUpdate();
				break;
			case 40:  // Down arrow
				event.preventDefault();
				historyIndex = Math.max(historyIndex - 1, -1);
				historyUpdate();
				break;
			case 27:  // Esc
				historyIndex = -1;
				historyBuffer = "";
				historyUpdate();
				break;
			default:
				if(historyIndex === -1){
					historyBuffer = input.value;
				}
		}
	});
}
