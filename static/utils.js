const SCHEME = window.location.protocol == "https:" ? "wss" : "ws";
const HOST = window.location.host;
const PATH = SCHEME + "://" + HOST;
const IMAGE_BASE_URL = "/cards/";

document.getElementById("socketPath").value = PATH;

let socket = false;
let socket_connected = false;

/*
 * Callback: called on the received data like callback(data)
 */
function ajaxGet(path, callback) {
    let xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState === XMLHttpRequest.DONE) {
            if (xmlhttp.status > 299) {
                console.log(xmlhttp.status);
                console.log(xmlhttp);
            }
            callback(xmlhttp.responseText);
        }
    };
    xmlhttp.open("GET", path, true);
    xmlhttp.send();
};

function ajaxPost(path, data, callback) {
    let xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState === XMLHttpRequest.DONE) {
            if (xmlhttp.status > 299) {
                console.log(xmlhttp.status);
                console.log(xmlhttp);
            }
            callback(xmlhttp.responseText);
        }
    };
    let formData = new FormData();
    for (var key in data) {
        if (data.hasOwnProperty(key)) {           
            formData.append(key, data[key]);
        }
    }
    xmlhttp.open("POST", path, true);
    xmlhttp.send(formData);
}

// Same as the ajaxOnce, calling a callback on the first websocket
// message received and then immediately closing
// I only have to do this b/c I didn't want to mess around with any
// webserver libraries in ~~Rust~~ Python oop
function websocketOnce(path, callback) {
    const socket_path = document.getElementById("socketPath");
    const full_path = socket_path.value + path;
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
function on_open() {
    add_to_output("### Opened WebSocket");
    const socket_connected_log = document.getElementById("socketConnect");
    socket_connected_log.innerHTML = "Yes";
    socket_connected = true;
}

/// Send closed status messages.
function on_close() {
    add_to_output("### Closed WebSocket");
    const socket_connected_log = document.getElementById("socketConnect");
    socket_connected_log.innerHTML = "No";
    socket_connected = false;
}

function has_all(obj, keys) {
    for (var i in keys) {
        let key = keys[i];
        if (!(key in obj)) {
            return false;
        }
    }
    return true;
}

/// Send socket message data to the output box.
function on_message(content) {
    console.log(content);
    let m = JSON.parse(content);
    if (!m) {
        console.log("Invalid JSON");
    } else {
        switch (m.type) {
            case "message":
                if (has_all(m, ["data"])) {
                    add_to_output("<<< " + m.data);
                } else {
                    console.log("Message had no data: " + content);
                }
                break;
            case "update":
                if (has_all(m, ["hand", "play"])) {
                    document.getElementById("hand-state").innerHTML = m.hand;
                    document.getElementById("play-state").innerHTML = m.play;
                } else {
                    console.log("Update lacked hand or play: " + content);
                }
                break;
            case "inspect":
                if (has_all(m, ["url", "title", "value", "flags", "tags"])) {
                    document.getElementById("inspect-image").src = IMAGE_BASE_URL + m.url;
                    document.getElementById("inspect-image").alt = m.title;
                    document.getElementById("inspect-title").innerHTML = m.title;
                    document.getElementById("inspect-value").innerHTML = m.value;
                    document.getElementById("inspect-flags").innerHTML = m.flags;
                    document.getElementById("inspect-tags").innerHTML = m.tags;
                } else {
                    console.log("Inspect lacked url, title, value, or flags: " + content);
                }
                break;
            case "choices":
                if (has_all(m, ["choices"])) {
                    choices = m.choices;
                    add_to_output("<<< " + formatChoices(choices));
                } else {
                    console.log("Choices lacked choices: " + content);
                }
            default:
                console.log("Weird request: " + content);
        }
    }
}

/// Set the socket callbacks.
function init_socket(socket) {
    socket.onopen = on_open;
    socket.onclose = on_close;
    socket.onmessage = (raw) => on_message(raw.data);
}

/// Connect to a socket on the address in the address input field.
function connect() {
    add_to_output("### Trying to open new WebSocket");
    if (socket_connected) {
        disconnect();
    }
    const socket_path = document.getElementById("socketPath");
    socket = new WebSocket(socket_path.value);
    init_socket(socket);
}

/// Close the socket.
function disconnect() {
    add_to_output("### Manually Closed WebSocket");
    socket.close();
}

/// Send data on the socket.
function send_on_websocket(what) {
    console.log(what);
    if (!socket_connected) {
        add_to_output("### Can't send to closed socket");
    } else {
        socket.send(what);
    }
}

/// Add the string to the output box on the next line.
function add_to_output(s) {
    const output = document.getElementById("output");
    output.innerHTML += "\n" + s;
    output.scrollTop = output.scrollHeight;
}

function dragstart_handler(ev) {
    const area_id = ev.target.dataset.area_id;
    const index = ev.target.dataset.card_index;
    ev.dataTransfer.setData("text/card_area", area_id);
    ev.dataTransfer.setData("text/card_index", index);
    //do_submit(inspect({}, [card.area.id, index]), "auto inspect");
}

function dragover_handler(ev) {
    ev.preventDefault();
    ev.dataTransfer.dropEffect = "move";
}

function drop_handler(moved_to_id, ev) {
    ev.preventDefault();
    let area_id = ev.dataTransfer.getData("text/card_area");
    let index = ev.dataTransfer.getData("text/card_index");
    do_submit(move({}, [area_id, index, moved_to_id]), "auto move");
}
