import asyncio
import argparse
from http import HTTPStatus
import json
import os
from typing import Callable, List
import websockets
from websockets.exceptions import ConnectionClosedError

from objects import AreaFlag, Player
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


async def send_choices(websocket, choices):
    await send_json(websocket, {
        "type": "choices",
        "choices": choices
    })


def format_card(index, card):
    return f" <span class='card-click' onclick='send_on_websocket(JSON.stringify(parse(\"inspect {card.area.id} {index}\").data));'><span class=\"index\">[{index}]</span> <span class=\"card-title\">{card.name}</span></span>"


def format_player(player_name):
    return f"<span class=\"playerName\">{player_name}</span>"


def format_score(score):
    return f"<span class=\"tag score {'negative-score' if score < 0 else 'non-negative-score'}\">({score} points)</span>"


def format_area(engine, player, area):
    can_look, area_contents = engine.kernel.look_at(player, area)
    if can_look:
        output = f"{format_area_id(area)} "
        if AreaFlag.PLAY_AREA in area.flags:
            output += format_score(engine.kernel.score_area(area))
        else:
            output += "<span class=\"tag visible\">(visible)</span>"
        output += "\n"

        for i in range(len(area_contents)):
            card = area_contents[i]
            output += format_card(i + 1, card) + "\n"

        return output[:-1]
    else:
        return f"{format_area_id(area)} <span class=\"tag card-count\">({area_contents} cards)</span>"


def format_area_id(area):
    classes = "area"
    area_id = area.id

    if '.' in area_id:
        dot_loc = area_id.index('.')
        first = area_id[:dot_loc]
        second = area_id[dot_loc:]
        area_id = f'{format_player(first)}{second}'

    if AreaFlag.PLAY_AREA in area.flags:
        classes += " playArea"
    if AreaFlag.DRAW_AREA in area.flags:
        classes += " drawArea"
    if AreaFlag.HAND_AREA in area.flags:
        classes += " handArea"
    if AreaFlag.DISCARD_AREA in area.flags:
        classes += " discardArea"

    return f'<span class="{classes}">{area_id}</span>'


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

        if self.started.set():
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
                    await send_message(client, message)
                except ConnectionClosedError:
                    pass
            else:
                print(f"Player {player.username} was in list to receive message, but they're no longer connected!")

    async def kernel_get_player_input(self, player: Player, choices: List[str], callback: Callable[[str], None]):
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


class RoomManager():
    def __init__(self):
        self.rooms = dict()

    async def make_room(self, websocket, room_name):
        print(f"make_room {room_name}")
        room = Room(room_name)
        self.rooms[room_name] = room
        self.rooms[room_name].engine.reset(room.kernel_send_message, room.kernel_get_player_input)
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
        await room.broadcast_message(f"{format_player(player_name)} has joined the room!")
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
            comment = data.get("comment", None).replace("&", '&amp;').replace("<", '&lt;').replace(">", '&gt;').replace("\"", '&quot;').replace("\'", '&#39;').replace("/", '&#x2F;');

            if comment:
                await room.broadcast_message(f"{format_player(player_name)} ended their turn \"{comment}\"")
            else:
                await room.broadcast_message(f"{format_player(player_name)} ended their turn")

        elif cmd == "move":
            from_area_id = data["src"]
            to_area_id = data["dst"]
            index = data["index"] - 1

            player = room.engine.get_player(player_name)
            from_area = room.engine.get_area(from_area_id)
            if from_area is None:
                await send_message(websocket, f"Source area '{from_area_id}' does not exist!")
                return

            index = data["index"] - 1
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
            area_id = data["area"]
            index = data["index"] - 1

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
            await room.broadcast_message(f"{format_player(player_name)} looked at card {index + 1} in {format_area_id(area)}")
        elif cmd == "choose":
            index = data["which"] - 1

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
                
                #await room.broadcast_update()  # TODO: Make this work right. Goal is to push an update after callback is called.
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
        room.engine.kernel.end_game()
        await room.broadcast_update(final=True)

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
