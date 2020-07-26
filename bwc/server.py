import argparse
import asyncio
import json
from numbers import Number
import os
from sanic import Sanic, response
from sanic.websocket import WebSocketProtocol
import sys
from typing import Callable, List, Optional, Tuple, Union
from websockets import ConnectionClosedError

from engine import Engine
from objects import Player
from server_rendering import *
from util import is_valid_player_name, is_valid_room_name, random_id

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOT_FOUND_CARD = "/placeholder-card.png"

async def send_json(websocket, data):
    await websocket.send(json.dumps(data))

async def send_card(websocket, card):
    card_image = card.image
    if card.image is None:
        card_image = NOT_FOUND_CARD

    flags_string = ", ".join([f.value for f in card.flags])
    tags_string = ", ".join(card.tags)

    await send_json(websocket, {
        "type": "inspect",
        "url": card_image,
        "title": card.name,
        "value": card.val,
        "flags": flags_string,
        "tags": tags_string
    })

def wrap_message(message):
    return {
        "type": "message",
        "data": message
    }

async def send_message(websocket, message):
    await send_json(websocket, wrap_message(message))


async def send_choices(websocket, choices):
    await send_json(websocket, {
        "type": "choices",
        "choices": choices
    })


async def send_update(websocket, engine, player):
    hand_field = ""
    play_field = ""

    for area in engine.game.all_areas.values():
        if AreaFlag.PLAY_AREA in area.flags:
            play_field += format_area(engine, player, area) + "\n\n"
        else:
            hand_field += format_area(engine, player, area) + "\n\n"

    hand_field = hand_field.strip()
    play_field = play_field.strip()

    await send_json(websocket, {
        "type": "update",
        "hand": hand_field,
        "play": play_field
    })


async def send_final_update(websocket, engine, player):
    hand_field = ""
    play_field = ""

    for player in engine.game.players.values():
        score = engine.kernel.score_player(player)
        play_field += f"{format_player(player)}: {format_score(score)}\n"

    play_field += "\n"

    # Do the rest of the update like normal
    for area in engine.game.all_areas.values():
        if AreaFlag.PLAY_AREA in area.flags:
            play_field += format_area(engine, player, area) + "\n\n"
        else:
            hand_field += format_area(engine, player, area) + "\n\n"

    hand_field = hand_field.strip()
    play_field = play_field.strip()

    await send_json(websocket, {
        "type": "update",
        "hand": hand_field,
        "play": play_field
    })

def parse_names_or_error(request) -> Tuple[bool, Union[Tuple[str, str], Tuple[str, int]]]:
    """
    REQUIRES: request is a request object made by Sanic
    ENSURES: returns (success, data)
        if success == True: data = (player_name, room_name)
        if success == False: data = (error_message, http_code)
    """
    res = get_fields(request.args, ("p", "room"))
    if res is None:
        return False, (f"Invalid arguments {request.args}", 400)

    player_name, room_name = res

    if not is_valid_room_name(room_name):
        return False, (f"Invalid room name '{room_name}'", 400)
    if not is_valid_player_name(player_name):
        return False, (f"Invalid player name '{player_name}'", 400)

    return True, (player_name, room_name)

class Room():
    def __init__(self, name):
        self.name = name
        self.engine = Engine()
        self.clients = dict()

        self.started = asyncio.Event()
        self.stopped = asyncio.Event()

        self.turn_over = asyncio.Event()

        self.active_choices = dict()
        self.last_choice = dict()
        self.choice_condition = asyncio.Condition()

    async def add_player(self, websocket, player_name):
        if player_name in self.clients:
            await send_message(websocket, f"Error: '{format_player(player_name)}' is already a player in this room '{self.name}!")
            return False

        if self.started.is_set():
            await send_message(websocket, f"Error: room '{self.name}' has already started!")
            return False

        self.clients[player_name] = websocket
        self.engine.add_player(player_name)

        return True

    async def broadcast_message(self, message):
        for client in self.clients.values():
            try:
                await send_message(client, message)
            except ConnectionClosedError:
                # Currently, if another client is disconnected, this could cause
                # any client that tries to broadcast to them to also get disconnected
                # because the disconnected client will throw a "DisconnectedError" or
                # something inside the stil-connected client
                # So, we ignore that and error and let the handler in the main code
                # take care of removing clients
                pass

    async def broadcast_update(self, final=False):
        for player_name, client in self.clients.items():
            player = self.engine.get_player(player_name)
            try:
                if final:
                    await send_final_update(client, self.engine, player)
                else:
                    await send_update(client, self.engine, player)
            except ConnectionClosedError:
                # Same as in broadcast_message
                pass

    def remove_player(self, player_name):
        if player_name in self.clients:
            self.engine.remove_player(player_name)
            del self.clients[player_name]

    async def kernel_send_message(self, players: List[Player], message: str):
        for player in players:
            client = self.clients.get(player.username, None)
            if client is not None:
                try:
                    await send_message(client, f"<span class='card-message'>{message}</span>")
                except ConnectionClosedError:
                    pass
            else:
                print(f"Player {player.username} was in list to receive message, but they're no longer connected!")

    async def kernel_get_player_input(self, player: Player, choices: List[str], callback: Callable[[str], None]):
        # make a copy just in case
        choices = choices[:]
        client = self.clients.get(player.username, None)
        if client is None:
            print(f"Player {player.username} was supposed to choose something, but they're no longer connected!")

        async with self.choice_condition:
            self.active_choices[player.username] = choices
            await send_choices(client, choices)
            # Use fancy asyncio magic to make sure that we only continue
            # once our player has made a choice
            await self.choice_condition.wait_for(lambda: player.username in self.last_choice)
            chosen_index = self.last_choice[player.username]
            del self.last_choice[player.username]
            del self.active_choices[player.username]

        callback(choices[chosen_index])
        await self.broadcast_update()


"""
Returns: None is data is missing any of fields, Some(tuple) containng the
extracted data otherwise
"""
def get_fields(data: dict, fields: Tuple[str, ...]) -> Optional[Tuple[str, ...]]:
    output = tuple(map(lambda field: data.get(field, None), fields))

    if any(value is None for value in output):
        return None
    else:
        return output


class RoomManager():
    def __init__(self):
        self.rooms = dict()

    def make_room(self, player_name, room_name) -> Tuple[str, int]:
        print(f"make_room {room_name}")
        if room_name in self.rooms:
            return f"Room '{room_name}' already exists!", 409

        room = Room(room_name)
        self.rooms[room_name] = room
        self.rooms[room_name].engine.reset(room.kernel_send_message, room.kernel_get_player_input)

        return f"Made room {room_name}", 200

    async def join_room(self, websocket, player_name, room_name):
        print(f"join_room {room_name} {player_name}")
        room = self.rooms.get(room_name, None)
        if room is None:
            await send_message(websocket, f"Error: room '{room_name}' does not exist!")
            return

        if not is_valid_player_name(player_name):
            await send_message(websocket, f"Player name '{player_name}' is invalid! Only numbers and lowercase letters allowed, no whitespace!")
            return

        if not await room.add_player(websocket, player_name):
            return

        await send_message(websocket, f"Joining room '{room_name}'...")
        await room.broadcast_message(f"{format_player(player_name)} has joined the room!")
        # Refresh the screen for everyone
        await room.broadcast_update()

        await room.started.wait()

        game_over = asyncio.create_task(room.stopped.wait())
        get_command = asyncio.create_task(websocket.recv())
        while True:
            # Wait on both tasks concurrently, return whichever one completes
            # first
            done, pending = await asyncio.wait(
                {
                    game_over,
                    get_command,
                },
                return_when=asyncio.FIRST_COMPLETED
            )

            if game_over in done:
                break
            elif get_command in done:
                response = get_command.result()
                response = json.loads(response)
                cmd = response.get("cmd", None)

                # Probably need to refresh the task before yielding execution
                # to other coroutines, so doing that just in case
                get_command = asyncio.create_task(websocket.recv())
                await self.handle_command(websocket, room, player_name, cmd, response)
            else:
                print("Congratulations, you reached the unreachable branch! Asyncio went funky")

        await send_message(websocket, "Game is over, you may leave now")

    async def handle_command(self, websocket, room, player_name, cmd, data):
        if cmd == "end":
            can_end = room.engine.kernel.end_turn(room.engine.get_player(player_name))
            if not can_end:
                await send_message(websocket, "You are not allowed to end your turn!")
                return

            room.turn_over.set()
            comment = data.get("comment", None)

            if comment is None:
                await room.broadcast_message(f"{format_player(player_name)} ended their turn \"{comment}\"")
            elif isinstance(comment, str):
                comment = comment.replace("&", '&amp;').replace("<", '&lt;').replace(">", '&gt;').replace("\"", '&quot;').replace("\'", '&#39;').replace("/", '&#x2F;')
                await room.broadcast_message(f"{format_player(player_name)} ended their turn")

        elif cmd == "move":
            res = get_fields(data, ("src", "dst", "index"))
            if res is None:
                error = f"Malformed move message from client: {data}"
                print(error)
                await send_message(websocket, error)
                return

            from_area_id, to_area_id, index = res

            if not isinstance(index, Number):
                index = int(index)
            index = index - 1

            player = room.engine.get_player(player_name)
            from_area = room.engine.get_area(from_area_id)
            if from_area is None:
                await send_message(websocket, f"Source area '{from_area_id}' does not exist!")
                return

            if index < 0 or index >= len(from_area.contents):
                await send_message(websocket, f"Index {index + 1} is out of range for area {format_area_id(from_area)}!")
                return

            card = from_area.contents[index]
            to_area = room.engine.get_area(to_area_id)
            if to_area is None:
                await send_message(websocket, f"Destination area '{to_area_id}' does not exist!")
                return

            can_move = room.engine.kernel.move_card(player, card, from_area, to_area)
            if not can_move:
                await send_message(websocket, "You cannot move this card!")
            else:
                # The kernel moves the card if it succeeds, no need to do anything else
                await room.broadcast_update()
                await room.broadcast_message(f"{format_player(player_name)} moved card {index + 1} from {format_area_id(from_area)} to {format_area_id(to_area)}")

        elif cmd == "inspect":
            player = room.engine.get_player(player_name)
            res = get_fields(data, ("area", "index"))
            if res is None:
                error = f"Malformed inspect message from client: {data}"
                print(error)
                await send_message(websocket, error)
                return

            area_id, index = res

            if not isinstance(index, Number):
                index = int(index)
            index = index - 1

            area = room.engine.get_area(area_id)
            if area is None:
                await send_message(websocket, f"Area '{area_id}' does not exist!")
                return

            can_look, area_contents = room.engine.kernel.look_at(player, area)
            if not can_look:
                await send_message(websocket, f"You are not allowed to look at {format_area_id(area)}")
                return

            if index < 0 or index >= len(area_contents):
                await send_message(websocket, f"Index {index + 1} if out of bounds for {format_area_id(area)}")
                return

            card = area_contents[index]

            await send_card(websocket, card)
            # await room.broadcast_message(f"{format_player(player_name)} looked at card {index + 1} in {format_area_id(area)}")
        elif cmd == "choose":
            index = data.get("which", None)
            if index is None:
                error = f"Malformed choose message from client: {data}"
                print(error)
                await send_message(websocket, error)
                return

            if not isinstance(index, Number):
                index = int(index)
            index = index - 1

            if player_name not in room.active_choices:
                await send_message(websocket, "You don't have any active choices")
                return

            choices = room.active_choices[player_name]
            if index < 0 or index >= len(choices):
                await send_message(websocket, f"Index {index + 1} is not a valid choice! Please choose again")
                await send_choices(websocket, choices)
                return

            async with room.choice_condition:
                room.last_choice[player_name] = index
                room.choice_condition.notify_all()
        elif cmd == "say":
            message = data.get("msg", None)
            if message is None:
                message = random_id()

            message = f"{format_player(player_name)}: " + message
            # Send messages through the kernel in case cards block/edit them
            # or something in the future
            room.engine.kernel.send_message(list(room.engine.game.players.values()), message)
        else:
            await send_message(websocket, f"The command '{cmd}' is not supported on this server")

    def run_game(self, player_name, room_name) -> Tuple[str, int]:
        print(f"run_game {room_name}")
        # Note: due to the way websocketOnce works, we only get one message to
        # send back on **THIS** `websocket` object. `room` methods still work
        room = self.rooms.get(room_name, None)
        if room is None:
            return f"Error: room '{room_name}' does not exist!", 404

        if room.started.is_set():
            return f"Error: room '{room_name}' is already in progress!", 409

        # Doesn't hold up this coroutine, schedules run automatically
        asyncio.create_task(self.game_mainloop(room, player_name, room_name))
        return "Game should be starting now!", 200

    async def game_mainloop(self, room, player_name, room_name):
        room.started.set()
        await room.broadcast_message(f"Starting game '{room_name}'...")

        room.engine.setup_game()

        while not room.engine.is_game_over():
            await room.broadcast_update()
            current_player = room.engine.game.current_player.username
            await room.broadcast_message(f"Current player: {format_player(current_player)}")

            room.turn_over.clear()
            await room.turn_over.wait()

            room.engine.advance_turn()

        room.engine.kernel.end_game()
        await room.broadcast_update(final=True)
        # Wait to actually stop room until final update is send to everyone
        # is guaranteed to receive it
        room.stopped.set()

    def remove_from_room(self, player_name, room_name):
        print(f"Removing {player_name} from room '{room_name}'")
        room = self.rooms.get(room_name, None)
        if room is not None:
            room.remove_player(player_name)

    """
    Paths defined:
    * /make?p=<player_name>&room=<room_name>
        Makes a new room
    * /join?p=<player_name>&room=<room_name>
        Joins a room as a player
    * /start?p=<player_name>&room=<room_name>
        Starts a game in an already-created room
    """
    async def serve_make(self, request):
        print(f"serve_make {request=}")
        success, res = parse_names_or_error(request)
        if success:
            player_name, room_name = res
            message, http_code = self.make_room(player_name, room_name)
            return response.json(wrap_message(message), status=http_code)
        else:
            error_message, http_code = res
            return response.json(wrap_message(error_message), status=http_code)

    async def serve_join(self, request, websocket):
        print(f"serve_join {request=}")
        success, res = parse_names_or_error(request)
        if success:
            player_name, room_name = res
            try:
                await self.join_room(websocket, player_name, room_name)
            finally:
                self.remove_from_room(player_name, room_name)
        else:
            error_message, http_code = res
            await send_message(websocket, f"{http_code}: {error_message}")

    async def serve_start(self, request):
        print(f"serve_start {request=}")
        success, res = parse_names_or_error(request)
        if success:
            player_name, room_name = res
            message, http_code = self.run_game(player_name, room_name)
            return response.json(wrap_message(message), status=http_code)
        else:
            error_message, http_code = res
            return response.json(wrap_message(error_message), status=http_code)

# This code is now redundant, but keeping it for posterity's sake (i lov it so much uwu)
async def intercept_http(path, headers):
    prefixes = ['make', 'join', 'start']
    if any(path.lstrip('/').startswith(x) for x in prefixes):
        return  # let the websocket handle it

    if path == '/':
        path = '/index.html'

    suffix_to_type = {
        '.html': 'text/html; charset=utf-8',
        '.js': 'text/javascript',
        '.css': 'text/css',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.json': 'application/json',
        '.mp3': 'audio/mpeg',
        '.opus': 'audio/opus',
        '': 'text/plain',
    }
    # Otherwise, act as a static file server
    path = os.path.join('static', *path.split('/'))
    if not os.path.exists(path):
        print('event=http_get path="{}" event_result=404_not_found'.format(path))
        return HTTPStatus(404), b'', b'404 Not Found'
    with open(path, 'rb') as f:
        print('event=http_get path="{}" event_result=200_found'.format(path))
        content_type = suffix_to_type.get(os.path.splitext(path)[1], 'text/plain')
        return HTTPStatus(200), {'Ur-Bad': 'Yes', 'Content-Type': content_type}, f.read()


def make_parser():
    parser = argparse.ArgumentParser(description="Start the 1kbwc server")
    parser.add_argument('--port', type=int, default=8081)

    return parser


def make_server():
    app = Sanic("1kbwc")
    manager = RoomManager()
    app.add_route(manager.serve_make, '/make', methods=['GET', 'POST'])
    app.add_route(manager.serve_start, '/start', methods=['GET', 'POST'])
    app.add_websocket_route(manager.serve_join, '/join')
    app.static('/', os.path.join(PROJECT_ROOT, 'static', 'index.html'))
    app.static('/', os.path.join(PROJECT_ROOT, 'static'))
    return app


def main():
    args = make_parser().parse_args()
    app = make_server()
    app.run(host="0.0.0.0", port=args.port, protocol=WebSocketProtocol, workers=1)

if __name__ == "__main__":
    main()
