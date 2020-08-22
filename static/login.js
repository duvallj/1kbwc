let lastSelected = undefined;

function makeRoomItem(room_name) {
    return "<li onclick=\"selectRoom(this)\">" + room_name + "</li>";
}

function selectRoom(element) {
    const gameList = document.getElementById("game-list");
    gameList.dataset.roomName = element.innerHTML;
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

function replacePage() {
    window.location.replace("play.html");
}

function setNameAndCreateRoom() {
    makeRoom(getNewRoom(), getName());
    replacePage();
}

function setNameAndJoinRoom() {
    joinRoom(getExistingRoom(), getName());
    replacePage();
}
