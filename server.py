import asyncio
import argparse
import websockets

def make_parser():
    parser = argparse.ArgumentParser(description="Start the 1kbwc server")
    parser.add_argument('--port', type=int, default=8081)

    return parser

async def hello(websocket, path):
    while True:
        name = await websocket.recv()
        print(f"< {name}")

        greeting = f"(at {path}): Hello {name}!"

        await websocket.send(greeting)
        print(f"> {greeting}")

def make_server(port):
    return websockets.serve(hello, "localhost", port)

def main():
    args = make_parser().parse_args()
    server = make_server(args.port)
    print(f"Listening on port {args.port}")
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
