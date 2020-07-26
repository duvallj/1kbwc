const MAKE_PATH = "/make";
const JOIN_PATH = "/join";
const START_PATH = "/start";


function validateRoom(room_name) {
    // All letters + digits, can have single dashes in between
    return /^[a-zA-Z0-9]+(\-[a-zA-Z0-9]+)*$/.test(room_name);
}

function validatePlayer(player_name) {
    // All lowercase letters
    return /^[a-z]+$/.test(player_name);
}

function addQueryParamsToPath(path) {
    const roomName_input = document.getElementById("roomName");
    const playerName_input = document.getElementById("myName");
    const room_name = roomName_input.value;
    const player_name = playerName_input.value.toLowerCase();
    if (!validateRoom(room_name)) {
        add_to_output("%%% Error: room name " + room_name + " is invalid! Please enter something without spaces or special characters.");
        return null;
    }
    if (!validatePlayer(player_name)) {
        add_to_output("%%% Error: player name " + player_name + " is invalid! Please enter something in all lowercase with no spaces.");
        return null;
    }
    return path + "?p=" + player_name + "&room=" + room_name;
}

function makeRoom() {
    const call_path = addQueryParamsToPath(MAKE_PATH);
    if (call_path !== null) {
        ajaxGet(call_path, on_message);
        
        // We figured this should be default
        joinRoom();
    }
}

function startRoom() {
    const call_path = addQueryParamsToPath(START_PATH);
    if (call_path !== null) {
        ajaxGet(call_path, on_message);
    }
}

function joinRoom() {
    const call_path = addQueryParamsToPath(JOIN_PATH);
    if (call_path !== null) {
        const roomName_input = document.getElementById("roomName");
        const playerName_input = document.getElementById("myName");
        
        // Xtreme hacks, referencing something in a global scope that hasn't been defined yet
        playerName = playerName_input.value;
        add_to_output("### Trying to join room " + roomName_input.value + " as player " + playerName_input.value);
        if (socket_connected) {
            disconnect();
        }
        socket = new WebSocket(socket_path.value + call_path);
        init_socket(socket);
    }
}
