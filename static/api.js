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

function getAndValidateParams() {
    const roomName_input = document.getElementById("roomName");
    const playerName_input = document.getElementById("myName");
    const room_name = roomName_input.value;
    const player_name = playerName_input.value.toLowerCase();
    if (!validateRoom(room_name)) {
        add_to_output("### Error: room name " + room_name + " is invalid! Please enter something without spaces or special characters.");
        return null;
    }
    if (!validatePlayer(player_name)) {
        add_to_output("### Error: player name " + player_name + " is invalid! Please enter something in all lowercase with no spaces.");
        return null;
    }
    return {
        player_name: player_name,
        room_name: room_name,
    };
}

function addParamsToPath(path, params) {
    return path + "?player_name=" + params.player_name + "&room_name=" + params.room_name;
}

function makeRoom() {
    const params = getAndValidateParams();
    if (params !== null) {
        ajaxPost(MAKE_PATH, params, function (message) {
            on_message(message)

            // We figured joining the room right after making it should be default
            // This is inside the callback to ensure we only try to join the room once it's
            // actually been made
            joinRoom();
        });
    }
}

function startRoom() {
    const params = getAndValidateParams();
    if (params !== null) {
        ajaxPost(START_PATH, params, on_message);
    }
}

function joinRoom() {
    const params = getAndValidateParams();
    if (params !== null) {
        // Protection in case someone accidentally clicks "join_room" again while they are the only person in the room
        if (socket_connected && roomName == params.room_name) {
            add_to_output("### You have already joined that room!");
            return;
        }

        const call_path = addParamsToPath(JOIN_PATH, params);
        
        // Xtreme hacks, referencing something in a global scope that hasn't been defined yet
        playerName = params.player_name;
        roomName = params.room_name;
        add_to_output("### Trying to join room " + params.room_name + " as player " + params.player_name);
        if (socket_connected) {
            disconnect();
        }
        socket = new WebSocket(socket_path.value + call_path);
        init_socket(socket);
    }
}
