const SCHEME = window.location.protocol == "https:" ? "wss": "ws";
const HOST = window.location.host;
const PATH = SCHEME + "://" + HOST + "/"

const socket_path = document.getElementById("socketPath");
socket_path.value = PATH;
const socket_connected_log = document.getElementById("socketConnect");
const input = document.getElementById("input");
const output = document.getElementById("output");

let socket = false;
let socket_connected = false;


function ajaxOnce(path, callback){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState === XMLHttpRequest.DONE ) {
            if (xmlhttp.status === 200) {
                callback(xmlhttp.responseText);
            }
            else {
                alert(xmlhttp.status);
            }
        }
    };
    xmlhttp.open("GET", path, true);
    xmlhttp.send();
};

// Same as the ajaxOnce, calling a callback on the first websocket
// message received and then immediately closing
// I only have to do this b/c I didn't want to mess around with any
// webserver libraries in ~~Rust~~ Python oop
function websocketOnce(path, callback) {
  const full_path = socket_path.value+path;
  var localsocket = new WebSocket(full_path);
 
  var has_received = false;

  localsocket.onopen = function () {
    add_to_output("### Did open websocket at " + full_path);
    // just in case??
    has_received = false;
  };

  localsocket.onmessage = function (message) {
    add_to_output("### Got websocket message");
    if (!has_received) {
      add_to_output("### Calling callback on websocket data");
      callback(message.data);
      has_received = true;
    }
    localsocket.close();
  };

  localsocket.onclose = function () {
    if (has_received) {
      add_to_output("### Got data successfully!");
    } else {
      add_to_output("### Did not get any data...");
    }
  }
};

/// Send opened status messages.
function on_open(){
	add_to_output("### Opened WebSocket");
	socket_connected_log.innerHTML = "Yes";
	socket_connected = true;
}

/// Send closed status messages.
function on_close(){
	add_to_output("### Closed WebSocket");
	socket_connected_log.innerHTML = "No";
	socket_connected = false;
}

/// Send socket message data to the output box.
function on_message(content){
	add_to_output("<<< " + content.data);
}

/// Set the socket callbacks.
function init_socket(socket){
	socket.onopen = on_open;
	socket.onclose = on_close;
	socket.onmessage = on_message;
}

/// Connect to a socket on the address in the address input field.
function connect(){
	add_to_output("### Trying to open new WebSocket");
	if(socket_connected){
		disconnect();
	}
	socket = new WebSocket(socket_path.value);
	init_socket(socket);
}

/// Close the socket.
function disconnect(){
  add_to_output("### Manually Closed WebSocket");
  socket.close();
}

/// Send data on the socket.
function send_on_websocket(what){
	console.log(what);
	if(!socket_connected){
		add_to_output("### Can't send to closed socket");
	}else{ 
		socket.send(what);
	}
}

/// Add the string to the output box on the next line.
function add_to_output(s){
	output.innerHTML += "\n" + s;
	output.scrollTop = output.scrollHeight;
}
