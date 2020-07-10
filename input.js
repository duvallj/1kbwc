const SCHEME = window.location.protocol == "https:" ? "wss": "ws";
const HOST = window.location.host;
const PATH = SCHEME + "://" + HOST + "/"

const socket_path = document.getElementById("socketPath");
socket_path.value = PATH;
const page_log = document.getElementById("log");
const socket_connected_log = document.getElementById("socketConnect");
// const message_input = document.getElementById("messageInput");
const input = document.getElementById("input");
const output = document.getElementById("output");

let socket = false;
let socket_connected = false;

/// Send opened status messages.
function on_open() {
  addToOutput("### Opened WebSocket");
  socket_connected_log.innerHTML = "Yes";
  socket_connected = true;
}

/// Send closed status messages.
function on_close() {
  addToOutput("### Closed WebSocket");
  socket_connected_log.innerHTML = "No";
  socket_connected = false;
}

/// Send socket message data to the output box.
function on_message(content) {
  addToOutput(content.data);
}

/// Set the socket callbacks.
function init_socket(socket) {
  socket.onopen = on_open;
  socket.onclose = on_close;
  socket.onmessage = on_message;
}

/// Connect to a socket on the address in the address input field.
function connect() {
  addToOutput("### Trying to open new WebSocket");
  if (socket_connected) {
    disconnect();
  }
  socket = new WebSocket(socket_path.value);
  init_socket(socket);
}

/// Close the socket.
function disconnect() {
  addToOutput("### Manually Closed WebSocket");
  socket.close();
}

/// Send data on the socket.
function send_on_websocket(what) {
  if (!socket_connected) {
    addToOutput("### Can't send to closed socket");
  }
  else { 
    socket.send(what);
  }
}

/// Process the input field when the button is clicked.
function on_submit(){
	let v = input.value;
	console.log(v);
	if(v){
		if(try_send(v)){
			addToOutput(v);
		}else{
			addToOutput("Failed to parse: " + v);
		}
		input.value = "";
	}
}

/// Check if the input can be made into a valid command, and sends it if it can.
function try_send(v){
	if(!v){
		console.log("no input");
		return false;
	}
	let matches = v.match(/[^\s"']+|"([^"]*)"|'([^']*)'/g);
	if(!matches){
		console.log("no matches");
		return false;
	}
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
	let command = tokens[0];
	let args = tokens.slice(1);
	console.log("tokens: " + tokens);
	console.log("command: " + command);
	console.log("args: " + args);
	let req = build_request(command, args);
	if(!req){
		console.log("bad details");
		return false;
	}
	if(req.command !== "help"){
		let to_send = JSON.stringify(req);
		send_on_websocket(to_send);
	}
	return true;
}

/// Build a request object from the given data, if possible.
function build_request(command, args){
	switch(command.toLowerCase()){
		case "help":
			if(args.length === 0){
				addToOutput("Commands available:");
				addToOutput(" - help [command]");
			}
			break;
		case "look":  // Request permission to look at target area. arg0: area
			if(args.length === 1){
				// TODO: Validate playername/area?
				return {command: "look", target: args[0]}
			}
			if(args.length === 0){
				// TODO: Ask for more
				return;
			}
			return;
		case "inspect":  // 
		
		default:
			return;
	}
}

/// Add the string to the output box on the next line.
function addToOutput(s){
	output.innerHTML += "\n" + s;
	output.scrollTop = output.scrollHeight;
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
