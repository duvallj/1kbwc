// Validates a room name against a regex. Should be the same regex as in bwc/util.py
function validateRoom(room_name) {
    // All letters + digits, can have single dashes in between
    return /^[a-zA-Z0-9]+(\-[a-zA-Z0-9]+)*$/.test(room_name);
}

// Validates a player name against a regex. Should be the same regex as in bwc/util.py
function validatePlayer(player_name) {
    // All lowercase letters
    return /^[a-z]+$/.test(player_name);
}

// Given a room and player name (that may not even be strings), validate them and print an error visible to the user
// if they are invalid. Returns `null` on all invalid, non-null on valid names.
function validateParams(maybe_room_name, maybe_player_name) {
    if (!maybe_room_name) {
        add_to_output("### Error: you must select a room name");
        return null;
    }
    if (!maybe_player_name) {
        add_to_output("### Error: you must select a player name");
        return null;
    }
    const room_name = maybe_room_name;
    const player_name = maybe_player_name.toLowerCase();

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

// Creates a path for a GET request given valid params from validateParams
function addParamsToPath(path, params) {
    return path + "?player_name=" + params.player_name + "&room_name=" + params.room_name;
}

/* Validates parameters, and returns a continuation function if they OK. Returns `null` otherwise.
 * This is to make it so we can handle parameter checking before other async stuff happens.
 * An example call would be:
```javascript
const callback = makeRoom(unchecked_room_name, unchecked_player_name);
if (callback) {
    doAsyncFunctionWith(callback);
}
```
 * This call pattern is shared with startRoom and joinRoom as well.
 */
function makeRoom(room_name, player_name) {
    const MAKE_PATH = "/make";
    
    const params = validateParams(room_name, player_name);
    if (params !== null) {
        return (() => {
            ajaxPost(MAKE_PATH, params, function (message) {
                on_message(message)

                // We figured joining the room right after making it should be default
                // This is inside the callback to ensure we only try to join the room once it's
                // actually been made
                const second_callback = joinRoom(room_name, player_name);
                if (second_callback) {
                    second_callback();
                } else {
                    console.log("Error joining room after making it!");
                }
            });
        });
    }

    return null;
}

function startRoom(room_name, player_name) {
    const START_PATH = "/start";
    
    const params = validateParams(room_name, player_name);
    if (params !== null) {
        return (() => { ajaxPost(START_PATH, params, on_message); });
    }
    
    return null;
}

function joinRoom(room_name, player_name) {
    const JOIN_PATH = "/join";
    
    const params = validateParams(room_name, player_name);
    if (params !== null) {
        // Protection in case someone accidentally clicks "join_room" again while they are the only person in the room
        // No longer needed because there is no join room button on the play page anymore, but keeping just in case
        if (socket_connected && currentRoomName == params.room_name) {
            add_to_output("### You have already joined that room!");
            return null;
        }

        return (() => {
            const call_path = addParamsToPath(JOIN_PATH, params);
            
            // Xtreme hacks, referencing something in a global scope that hasn't been defined yet
            currentPlayerName = params.player_name;
            currentRoomName = params.room_name;
            add_to_output("### Trying to join room " + params.room_name + " as player " + params.player_name);
            if (socket_connected) {
                disconnect();
            }
            const socket_path = document.getElementById("socketPath");
            socket = new WebSocket(socket_path.value + call_path);
            init_socket(socket);
        });
    }

    return null;
}

// Call a callback on the data received from a request to list rooms
function listRooms(callback) {
    const LIST_PATH = "/list";
    
    ajaxGet(LIST_PATH, callback);
}
