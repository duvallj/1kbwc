let choices = [];  // Options for the choice state, empty indicates non-choice state
let playerName = "nonexistent";

/// Process the input field when the button is clicked.
function on_submit(){
	let v = input.value;
	console.log(v);
	if(v){
		let r = parse(v);
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

function parse(v){
	let r = {
		data: "",
		send: false,
		output: "none",
		clear: true
	};
	
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
			return help(r, args)
			break;
		case "draw":
			if(args.length === 0){
				args = ["drawpile", 1, playerName + ".hand"];
				return move(r, args);
			}
			r.output = "fail";
			return r;
			break;
		case "play":
			if(args.length === 2){
				args.unshift(playerName + ".hand");
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
			break;
		case "end":
			return end(r, args);
			break;
		case "inspect":
			if(args.length === 2){
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
			break;
		case "discard":
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
			break;
		case "move":
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
			break;
		default:
			r.output = "fail";
			return r;
	}
	console.log("what.");
}

function help(r, args){
	if(args.length === 0){
		r.data = "Commands available:"
		let cmds = Object.keys(HELPSTRINGS);
		for(let i = 0; i < cmds.length; ++i){
			r.data += "\n - " + HELPSTRINGS[cmds[i]].usage;
		}
		r.output = "data";
	}else{
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

/// Send command on enter.
window.onload = function(){
	input.addEventListener("keyup", function(event){
		if(event.keyCode === 13){
			event.preventDefault();
			document.getElementById("submit").click();
		}
	});
}
