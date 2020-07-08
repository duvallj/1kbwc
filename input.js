const SCHEME = window.location.protocol == "https:" ? "wss": "ws";
const HOST = window.location.host;
const PATH = SCHEME + "://" + HOST + "/"

const socket_path = document.getElementById("socketPath");
socket_path.value = PATH;
const page_log = document.getElementById("log");
const socket_connected_log = document.getElementById("socketConnect");
const message_input = document.getElementById("messageInput");

let socket = false;
let socket_connected = false;

function on_open() {
  addToOutput("### Opened WebSocket");
  socket_connected_log.innerHTML = "Yes";
  socket_connected = true;
}

function on_close() {
  addToOutput("### Closed WebSocket");
  socket_connected_log.innerHTML = "No";
  socket_connected = false;
}

function on_message(content) {
  addToOutput(content.data);
}

function init_socket(socket) {
  socket.onopen = on_open;
  socket.onclose = on_close;
  socket.onmessage = on_message;
}

function connect() {
  addToOutput("### Trying to open new WebSocket");
  if (socket_connected) {
    disconnect();
  }
  socket = new WebSocket(socket_path.value);
  init_socket(socket);
}

function disconnect() {
  addToOutput("### Manually Closed WebSocket");
  socket.close();
}

function send_on_websocket(what) {
  if (!socket_connected) {
    addToOutput("### Can't send to closed socket");
  }
  else { 
    socket.send(what);
  }
}

function processCommand(){
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
		let to_send = JSON.stringify({"command": command, "args": args});
		send_on_websocket(to_send);
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
