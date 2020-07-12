import asyncio
import argparse
import json
import websockets
from objects import Card, Area, Game
from engine import Engine

def make_parser():
    parser = argparse.ArgumentParser(description="Start the 1kbwc server")
    parser.add_argument('--port', type=int, default=8081)

    return parser

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
            await websocket.send(f"Error: '{player_name}' is already a player in this room '{room_name}!")
            return False

        if self.started.set():
            await websocket.send(f"Error: room '{room_name}' has already started!")
            return False

        self.clients[player_name] = websocket
        self.engine.add_player(player_name)

        return True

    async def broadcast_message(self, message):
        await asyncio.gather(
                *[client.send(message) for _, client in self.clients.items()])


class RoomManager():
    def __init__(self):
        self.rooms = dict()

    async def make_room(self, websocket, room_name):
        print(f"make_room {room_name}")
        self.rooms[room_name] = Room(room_name)
        self.rooms[room_name].engine.reset()
        await websocket.send(f"Made room {room_name}")

    async def join_room(self, websocket, room_name, player_name):
        print(f"join_room {room_name} {player_name}")
        room = self.rooms.get(room_name, None)
        if room is None:
            await websocket.send(f"Error: room '{room_name}' does not exist!")
            return

        if not await room.add_player(websocket, player_name):
            return

        await websocket.send(f"Joining room '{room_name}'...")
        await room.started.wait()

        # TODO: write loop that takes care of receiving commands from this
        # websocket
        while not room.stopped.is_set():
            response = await websocket.recv()
            response = json.loads(response)
            cmd = response.get("cmd", None)

            await self.handle_command(
                    websocket, room, player_name, cmd, response)

        await room.stopped.wait()

    def remove_from_room(self, room_name, player_name):
        pass

    async def handle_command(self, websocket, room, player_name, cmd, data):
        if cmd == "end":
            can_end = room.engine.kernel.end_turn(room.engine.get_player(player_name))
            if not can_end:
                await websocket.send("You are not allowed to end your turn!")
                return 

            room.turn_over.set()
            comment = response.get("comment", None)
            if comment:
                await room.broadcast_message(f"Player {player_name} ended their turn")
            else:
                await room.broadcast_message(f"Player {player_name} ended their turn \"{comment}\"")

        elif cmd == "move":
            player = room.engine.get_player(player_name)
            from_area = room.engine.get_area(data["src"])
            index = data["index"] - 1
            if index <= 0 or index > len(from_area.contents):
                await websocket.send(f"Index {index} is out of range for area {data['src']}!")
                return
            
            to_area = room.engine.get_area(data["dst"])

            can_move = room.engine.kernel.move_card(player, from_area, to_area)
            if not can_move:
                await websocket.send("You cannot move this card!")
                return

            # The kernel moves the card if it succeeds, no need to do anything else

        elif cmd == "inspect":
            player = room.engine.get_player(player_name)
            area = room.engine.get_area(dst["area"])

            area_contents = room.engine.kernel.look_at(player, area)

        else:
            await websocket.send(f"The command '{cmd}' is not supported on this server")

    async def run_game(self, websocket, room_name):
        print(f"run_game {room_name}")
        room = self.rooms.get(room_name, None)
        if room is None:
            await websocket.send(f"Error: room '{room_name}' does not exist!")
            return

        room.started.set()
        await room.broadcast_message(f"Starting game '{room_name}'...")

        room.engine.setup_game()
        # TODO: write the game loop better
        while not room.engine.is_game_over():
            current_player = room.engine.game.current_player.username
            await room.broadcast_message(f"Current player: {current_player}")
            
            room.turn_over.clear()
            await room.turn_over.wait()

            room.engine.advance_turn()

        room.stopped.set()

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
        print(path)
        if path.startswith("/make/"):
            rest = path[6:]
            await self.make_room(websocket, rest)
        elif path.startswith("/join/"):
            rest = path[6:].split("/")
            if len(rest) != 2:
                await websocket.send(f"Invalid number of arguments in {path}")
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
            await websocket.send("Game should be starting now!")

def make_server(port):
    manager = RoomManager()
    return websockets.serve(manager.serve, "localhost", port)

def main():
    args = make_parser().parse_args()
    server = make_server(args.port)
    print(f"Listening on port {args.port}")
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
