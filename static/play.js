// From play-setup.js, if this file is executed as the window is loading, make sure we still run setup
window.onload = playSetup;

// Global input element
let input = document.getElementById("input");

let choices = [];  // Options for the choice state, empty indicates non-choice state

// Global data to control command history
let commandHistory = [];
let historyIndex = -1;
let historyBuffer = "";

// Function that gets called when the "Start Room" button is pressed
function actualStartRoom() {
    // Player and Room name arameters should have already been read from page as part of playSetup

    // So we just need to go through the parameter-checking callback flow
    const callback = startRoom(currentRoomName, currentPlayerName);
    if (callback) {
        callback();
    } else {
        console.log("Error starting room with player name " + currentPlayerName + " and room name " + currentRoomName);
    }
}

// Function that gets called when the "Disconnect" button is pressed
function actualDisconnect() {
    // First, make sure we close the websocket (defined in utils.js)
    disconnect();
    // Then, reload the page
    window.history.go();
}

/// Process the input field when the "enter" button is clicked.
function on_submit() {
    let v = input.value;
    console.log(v);
    if (v) {
        let r = {
            data: "",
            send: false,
            output: "none",
            clear: true
        };
        if (choices.length === 0) {
            // Parse the command as normal
            r = parse(r, tokenize(v));
        } else {
            // We have a choice to make, parse that instead
            r = choiceParse(r, tokenize(v));
        }
        do_submit(r, v);
    }
}

// Function that handles the parsed command
function do_submit(r, v) {
    if (r.output === "input") {
        add_to_output(">>> " + v);
    }
    if (r.output === "fail") {
        add_to_output("%%% Failed to parse: " + v);
    }
    if (r.output === "data") {
        add_to_output("%%% " + r.data);
    }
    if (r.send) {
        send_on_websocket(JSON.stringify(r.data));
    }
    if (r.clear) {
        input.value = "";
        commandHistory.unshift(v);
        historyIndex = -1;
        historyBuffer = "";
    }
}

const HELPSTRINGS = {
    "help": {
        "usage": "help [command]",
        "details": "Display the available commands, or help on specific commands."
    },
    "draw": {
        "usage": "draw",
        "details": "Draw a single card from the deck to your hand."
    },
    "play": {
        "usage": "play index dst",
        "details": "Play the card at `index` in your hand to `dst`."
    },
    "end": {
        "usage": "end [comment]",
        "details": "End your turn."
    },
    "inspect": {
        "usage": "inspect area index",
        "details": "Display the card in `area` at `index` in the inspect window."
    },
    "discard": {
        "usage": "discard area index",
        "details": "Discard the card in `area` at `index`."
    },
    "move": {
        "usage": "move src index dst",
        "details": "Move the card in `src` at `index` to `dst`."
    },
    "say": {
        "usage": "say [message]",
        "details": "Say something in chat for everyone to see! :3"
    }
}
const NOTENOUGHARGS = "Not enough arguments: ";

// Given a command as a string, tokenize it into elements on spaces, treating quoted elements as no spaces
function tokenize(v) {
    let matches = v.match(/[^\s"']+|"([^"]*)"|'([^']*)'/g);
    let tokens = [];
    for (let i = 0; i < matches.length; ++i) {
        console.log(i.toString() + " " + matches[i]);
        if (matches[i].charAt(0) === '"') {
            if (matches[i].length >= 3) {
                tokens.push(matches[i].slice(1, -1));
            } else {
                console.log("Invalid token: " + matches[i]);
                return false;
            }
        } else {
            tokens.push(matches[i]);
        }
    }
    return tokens;
}

// Given a list of tokens and output data `r`, parse the command contained in the tokens.
function parse(r, tokens) {
    if (tokens.length < 1) {
        r.output = "fail";
        return r;
    }

    let command = tokens[0];
    let args = tokens.slice(1);
    console.log("tokens: " + tokens);
    console.log("command: " + command);
    console.log("args: " + args);

    switch (command.toLowerCase()) {
        case "help":
        case "h":
            return help(r, args);
            break;
        case "draw":
        case "d":
            return draw(r, args);
            break;
        case "play":
        case "p":
            return play(r, args);
            break;
        case "end":
        case "e":
            return end(r, args);
            break;
        case "inspect":
        case "i":
            return readInspect(r, args);
            break;
        case "discard":
            return discard(r, args);
            break;
        case "move":
        case "m":
            return readMove(r, args);
            break;
        case "say":
        case "s":
            return doSay(r, args);
            break;
        default:
            r.output = "fail";
            return r;
    }
    console.log("what.");
}

// Similar to `parse`, but only accept commands that are valid while in a choosing state
function choiceParse(r, tokens) {
    if (tokens.length < 1) {
        r.output = "fail";
        return r;
    }

    let command = tokens[0];
    let num = parseInt(command);

    if (!isNaN(num)) {  // Choiche
        if (num < 1 || num > choices.length) {
            r.output = "data";
            r.data = "Index " + num.toString() + " is out of range.";
            return r;
        }
        // validdd
        r.send = true;
        r.output = "input";
        r.data = {
            "cmd": "choose",
            "which": num,
            "caller": currentPlayerName
        }
        choices = [];
        return r;
    }

    switch (command) {
        case "inspect":
        case "i":
            return readInspect(r, tokens.slice(1));
            break;
        case "again":
        case "a":
            r.output = "data";
            r.data = formatChoices(choices);
            return r;
        default:
            r.output = "fail";
            return r;
    }
    console.log("what,");
}

// Given a list of choices, format them with the appropriate HTML tags for output
function formatChoices(c) {
    s = "Options:";
    for (let i = 0; i < c.length; ++i) {
        s += `\n<span class="index"> [${i + 1}]</span> <span class="choiceOption">${c[i]}</span>`;
    }
    return s;
}

/// Parse and send a help command.
function help(r, args) {
    if (args.length === 0) {
        r.data = "Commands available:"
        let cmds = Object.keys(HELPSTRINGS);
        for (let i = 0; i < cmds.length; ++i) {
            r.data += "\n - " + HELPSTRINGS[cmds[i]].usage;
        }
        r.output = "data";
    } else {  // fixme: do something else if no commands are valid.
        let first = true;
        for (let i = 0; i < args.length; ++i) {
            if (HELPSTRINGS[args[i]]) {
                if (first) {
                    first = false;
                } else {
                    r.data += "\n";
                }
                r.data += HELPSTRINGS[args[i]].usage + "\n - " + HELPSTRINGS[args[i]].details;
            }
        }
        r.output = "data";
    }
    return r;
}

/// Parse and send a draw command.
function draw(r, args) {
    if (args.length === 0) {
        args = ["drawpile", 1, currentPlayerName + ".hand"];
        return move(r, args);
    }
    r.output = "fail";
    return r;
}

/// Parse and send a play command.
function play(r, args) {
    if (args.length === 2) {
        args.unshift(currentPlayerName + ".hand");
        if (args[2].indexOf('.') === -1) {  // Might be a player name
            if (document.getElementById("play-state").innerHTML.indexOf("<span class=\"currentPlayerName\">" + args[2] + "</span>") !== -1) {
                // There exists a player with the name in args[2]
                args[2] += ".play";
                console.log("modified play target to " + args[2]);
            }
        }
        return move(r, args);
    }
    if (args.length < 2) {
        r.data = NOTENOUGHARGS + HELPSTRINGS.play.usage;
        r.output = "data";
        r.clear = false;
        return r;
    }
    r.output = "fail";
    return r;
}

/// Parse and send an end turn request.
function end(r, args) {
    r.send = true;
    r.output = "input";
    r.data = {
        "cmd": "end",
        "caller": currentPlayerName,
        "comment": ""
    };
    if (args.length > 0) {
        r.data.comment = args.join(" ");
    }
    return r;
}

// Wrapper around `inspect` that allows shorthand specification of the current player's hand
function readInspect(r, args) {
    if (args.length === 2) {
        if (args[0] === "hand") {
            args[0] = currentPlayerName + ".hand";
        }
        return inspect(r, args);
    }
    if (args.length < 2) {
        r.data = NOTENOUGHARGS + HELPSTRINGS.inspect.usage;
        r.output = "data";
        r.clear = false;
        return r;
    }
    r.output = "fail";
    return r;
}

/// Parse and send an inspect command.
function inspect(r, args) {
    let area = args[0];
    let index = parseInt(args[1], 10);

    if (isNaN(index) || index < 0) {
        console.log("Bad index");
        r.output = "fail";
        return r;
    }

    r.send = true;
    r.output = "input";
    r.data = {
        "cmd": "inspect",
        "caller": currentPlayerName,
        "area": area,
        "index": index
    };
    return r;
}

// Shorthand command for moving a target card to the discard pile
function discard(r, args) {
    if (args.length === 2) {
        args.push("discard");
        return move(r, args);
    }
    if (args.length < 2) {
        r.data = NOTENOUGHARGS + HELPSTRINGS.discard.usage;
        r.output = "data";
        r.clear = false;
        return r;
    }
    r.output = "fail";
    return r;
}

// Wrapper function for `move` that checks for the correct number of arguments
function readMove(r, args) {
    if (args.length === 3) {
        return move(r, args);
    }
    if (args.length < 3) {
        r.data = NOTENOUGHARGS + HELPSTRINGS.move.usage;
        r.output = "data";
        r.clear = false;
        return r;
    }
    r.output = "fail";
    return r;
}

/// Parse and send a move.
function move(r, args) {
    let src = args[0];
    let index = parseInt(args[1], 10);
    let dst = args[2];

    if (isNaN(index) || index < 0) {
        console.log("Bad index");
        r.output = "fail";
        return r;
    }

    r.send = true;
    r.output = "input";
    r.data = {
        "cmd": "move",
        "caller": currentPlayerName,
        "src": src,
        "index": index,
        "dst": dst
    };
    return r;
}

/// Parse and send a message
function doSay(r, args) {
    r.send = true;
    r.output = "input";
    r.data = {
        "cmd": "say",
        "caller": currentPlayerName,
    };
    if (args.length > 0) {
        r.data.msg = args.join(" ");
    }
    return r;
}

/// Set the buffer to the proper value in the history, since something just changed.
function historyUpdate() {
    input.value = historyIndex >= 0 ? commandHistory[historyIndex] : historyBuffer;
}
