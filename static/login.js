let lastSelected = undefined;

function makeRoomItem(room_name) {
    return "<li onclick=\"selectRoom(this)\">" + room_name + "</li>";
}

function selectRoom(element) {
    const gameList = document.getElementById("game-list");
    const room_name = element.innerHTML;
    gameList.dataset.roomName = room_name;
    // For convenience, in case they want to make a similarly-named room
    const roomInput = document.getElementById("roomName");
    roomInput.value = room_name;

    if (lastSelected !== undefined) {
        lastSelected.classList.remove("game-list-selected");
    }
    element.classList.add("game-list-selected");
    lastSelected = element;
}

function populateRoomList() {
    listRooms(roomJSON => {
        console.log(roomJSON);

        const room_list = JSON.parse(roomJSON);
        let buf = "";
        for (const room_name of room_list) {
            buf += makeRoomItem(room_name);
        }
        document.getElementById("game-list").innerHTML = buf;
    });
}

window.onload = populateRoomList;

function getName() {
    const nameInput = document.getElementById("myName");
    return nameInput.value;
}

function getExistingRoom() {
    const gameList = document.getElementById("game-list");
    return gameList.dataset.roomName;
}

function getNewRoom() {
    const roomInput = document.getElementById("roomName");
    return roomInput.value;
}

function replacePage(room_name, player_name, callback) {
    const socket_path = document.getElementById("socketPath");
    const copied_socket_path_value = socket_path.value;
    ajaxGet("play.html", playHTML => {
        console.log("Replacing page...");
        document.write(playHTML);

        // Set up settings on the new page
        const new_socket_path = document.getElementById("socketPath");
        new_socket_path.value = copied_socket_path_value;
        const room_name_output = document.getElementById("roomName");
        room_name_output.value = room_name;
        const player_name_output = document.getElementById("myName");
        player_name_output.value = player_name;

        // Finally, do the thing
        callback();
    });
}

function setNameAndCreateRoom() {
    const room_name = getNewRoom();
    const player_name = getName();
    replacePage(room_name, player_name, () => {
        makeRoom(room_name, player_name);
    });
}

function setNameAndJoinRoom() {
    const room_name = getExistingRoom();
    const player_name = getName();
    replacePage(room_name, player_name, () => {
        joinRoom(room_name, player_name);
    });
}
