const MAKE_ROOM_PATH = "/make/";
const JOIN_ROOM_PATH = "/join/";
const START_ROOM_PATH = "/start/";

const roomName_input = document.getElementById("roomName");
const playerName_input = document.getElementById("playerName");

function makeRoom() {
    const call_path = MAKE_ROOM_PATH + roomName_input.value;
    websocketOnce(call_path, add_to_output);
}

function startRoom() {
    const call_path = START_ROOM_PATH + roomName_input.value;
    websocketOnce(call_path, add_to_output);
}

function joinRoom() {
    const call_path = JOIN_ROOM_PATH + roomName_input.value + '/' + playerName_input.value;
    // Xtreme hacks, referencing something in a global scope that hasn't been defined yet
    playerName = playerName_input.value;
	add_to_output("### Trying to join room " + roomName_input.value + " as player " + playerName_input.value);
	if(socket_connected){
		disconnect();
	}
	socket = new WebSocket(socket_path.value + call_path);
	init_socket(socket);
}
