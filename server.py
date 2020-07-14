import asyncio
import argparse
import json
from http import HTTPStatus

import websockets
import os
from websockets.exceptions import ConnectionClosedError
from objects import AreaFlag
from engine import Engine

NOT_FOUND_CARD = "/placeholder-card.png"


async def send_json(websocket, data):
    await websocket.send(json.dumps(data))


async def send_card(websocket, card):
    card_image = card.image
    if card.image is None:
        card_image = NOT_FOUND_CARD

    flags_string = ", ".join([f.value for f in card.flags])

    await send_json(websocket, {
        "type": "inspect",
        "url": card_image,
        "title": card.name,
        "value": card.val,
        "flags": flags_string
    })


async def send_message(websocket, message):
    await send_json(websocket, {
        "type": "message",
        "data": message
    })


def format_card(index, card):
    return f" <span class=\"index\">[{index}]</span> <span class=\"card-title\">{card.name}</span>"


def format_area(engine, player, area):
    can_look, area_contents = engine.kernel.look_at(player, area)
    if can_look:
        output = f"{markup_id(area)} "
        if AreaFlag.PLAY_AREA in area.flags:
            score = engine.kernel.score_area(area)
            output += f"<span class=\"tag score {'negative-score' if score < 0 else 'non-negative-score'}\">({score} points)</span>"
        else:
            output += "<span class=\"tag visible\">(visible)</span>"
        output += "\n"

        for i in range(len(area_contents)):
            card = area_contents[i]
            output += format_card(i + 1, card) + "\n"

        return output[:-1]
    else:
        return f"{markup_id(area)} <span class=\"tag card-count\">({area_contents} cards)</span>"

def markup_id(area):
    classes = "area"
    id = area.id
    if '.' in id:
        first = id[:id.index('.')]
        second = id[id.index('.'):]
        id = f'<span class="playerName">{first}</span>{second}'

    if AreaFlag.PLAY_AREA in area.flags:
        classes += " playArea"
    if AreaFlag.DRAW_AREA in area.flags:
        classes += " drawArea"
    if AreaFlag.HAND_AREA in area.flags:
        classes += " handArea"
    if AreaFlag.DISCARD_AREA in area.flags:
        classes += " discardArea"

    return f'<span class="{classes}">{id}</span>'

async def send_update(websocket, engine, player):
    hand_field = ""
    play_field = ""

    for area in engine.game.all_areas.values():
        if AreaFlag.PLAY_AREA in area.flags:
            play_field += format_area(engine, player, area) + "\n\n"
        else:
            hand_field += format_area(engine, player, area) + "\n\n"

    hand_field = hand_field[:-2]
    play_field = play_field[:-2]

    await send_json(websocket, {
        "type": "update",
        "hand": hand_field,
        "play": play_field
    })


class Room():
    def __init__(self, name):
        self.name = name
        self.engine = Engine()
        self.started = asyncio.Event()
        self.stopped = asyncio.Event()
        self.clients = dict()
        self.turn_over = asyncio.Event()

    async def add_player(self, websocket, player_name):
        if player_name in self.clients:
            await send_message(websocket, f"Error: '{player_name}' is already a player in this room '{room_name}!")
            return False

        if self.started.set():
            await send_message(websocket, f"Error: room '{room_name}' has already started!")
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

    async def broadcast_update(self):
        for player_name, client in self.clients.items():
            player = self.engine.get_player(player_name)
            try:
                print(f"broadcast_update to {player_name}")
                await send_update(client, self.engine, player)
            except ConnectionClosedError:
                # Same as in broadcast_message
                pass

    def remove_player(self, player_name):
        if player_name in self.clients:
            self.engine.remove_player(player_name)
            del self.clients[player_name]


class RoomManager():
    def __init__(self):
        self.rooms = dict()

    async def make_room(self, websocket, room_name):
        print(f"make_room {room_name}")
        self.rooms[room_name] = Room(room_name)
        self.rooms[room_name].engine.reset()
        await send_message(websocket, f"Made room {room_name}")

    async def join_room(self, websocket, room_name, player_name):
        print(f"join_room {room_name} {player_name}")
        room = self.rooms.get(room_name, None)
        if room is None:
            await send_message(websocket, f"Error: room '{room_name}' does not exist!")
            return

        if not await room.add_player(websocket, player_name):
            return

        await send_message(websocket, f"Joining room '{room_name}'...")
        await room.started.wait()

        # TODO: write loop that takes care of receiving commands from this
        # websocket
        while not room.stopped.is_set():
            response = await websocket.recv()
            response = json.loads(response)
            cmd = response.get("cmd", None)

            await self.handle_command(websocket, room, player_name, cmd, response)

        await send_message(websocket, "Game is over, you may leave now")

    async def handle_command(self, websocket, room, player_name, cmd, data):
        if cmd == "end":
            can_end = room.engine.kernel.end_turn(room.engine.get_player(player_name))
            if not can_end:
                await send_message(websocket, "You are not allowed to end your turn!")
                return

            room.turn_over.set()
            comment = data.get("comment", None)
            if comment:
                await room.broadcast_message(f"Player {player_name} ended their turn \"{comment}\"")
            else:
                await room.broadcast_message(f"Player {player_name} ended their turn")

        elif cmd == "move":
            player = room.engine.get_player(player_name)
            from_area = room.engine.get_area(data["src"])
            if from_area is None:
                await send_message(websocket, f"Source area '{data['src']}' does not exist!")
                return

            index = data["index"] - 1
            if index < 0 or index >= len(from_area.contents):
                await send_message(websocket, f"Index {index + 1} is out of range for area {data['src']}!")
                return

            card = from_area.contents[index]
            to_area = room.engine.get_area(data["dst"])
            if to_area is None:
                await send_message(websocket, f"Destination area '{data['dst']}' does not exist!")
                return

            can_move = room.engine.kernel.move_card(player, card, from_area, to_area)
            if not can_move:
                await send_message(websocket, "You cannot move this card!")
            else:
                # The kernel moves the card if it succeeds, no need to do anything else
                await room.broadcast_update()

        elif cmd == "inspect":
            player = room.engine.get_player(player_name)
            index = data["index"] - 1
            area = room.engine.get_area(data["area"])
            if area is None:
                await send_message(websocket, f"Area '{data['area']}' does not exist!")
                return

            can_look, area_contents = room.engine.kernel.look_at(player, area)
            if not can_look:
                await send_message(websocket, f"You are not allowed to look at area '{data['area']}'")
                return

            if index < 0 or index >= len(area_contents):
                await send_message(websocket, f"Index {index + 1} if out of bounds for area '{data['area']}'")
                return

            card = area_contents[index]

            await send_card(websocket, card)
        else:
            await send_message(websocket, f"The command '{cmd}' is not supported on this server")

    async def run_game(self, websocket, room_name):
        print(f"run_game {room_name}")
        room = self.rooms.get(room_name, None)
        if room is None:
            await send_message(websocket, f"Error: room '{room_name}' does not exist!")
            return

        room.started.set()
        await room.broadcast_message(f"Starting game '{room_name}'...")

        room.engine.setup_game()
        # TODO: write the game loop better
        while not room.engine.is_game_over():
            await room.broadcast_update()
            current_player = room.engine.game.current_player.username
            await room.broadcast_message(f"Current player: {current_player}")

            room.turn_over.clear()
            await room.turn_over.wait()

            room.engine.advance_turn()

        room.stopped.set()

    def remove_from_room(self, room_name, player_name):
        print(f"Removing {player_name} from room '{room_name}'")
        room = self.rooms.get(room_name, None)
        if room is not None:
            room.remove_player(player_name)

    """
    Paths defined:
    * /make/<room_name>
        Makes a new room
    * /join/<room_name>/<player_name>
        Joins a room as a player
    * /start/<room_name>
        Starts a game in an already-created room
    """

    async def serve(self, websocket, path):
        print(f"Websocket connected on {path}")
        if path.startswith("/make/"):
            rest = path[6:]
            await self.make_room(websocket, rest)
        elif path.startswith("/join/"):
            rest = path[6:].split("/")
            if len(rest) != 2:
                await send_message(websocket, f"Invalid number of arguments in {path}")
                return

            room_name, player_name = rest
            try:
                await self.join_room(websocket, room_name, player_name)
            finally:
                self.remove_from_room(room_name, player_name)

        elif path.startswith("/start/"):
            rest = path[7:]
            # Doesn't hold up this socket, schedules run automatically
            asyncio.create_task(self.run_game(websocket, rest))
            await send_message(websocket, "Game should be starting now!")


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


def make_server(port):
    manager = RoomManager()
    return websockets.serve(manager.serve, "0.0.0.0", port, process_request=intercept_http)


def main():
    args = make_parser().parse_args()
    server = make_server(args.port)
    print(f"Listening on port {args.port}")
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
