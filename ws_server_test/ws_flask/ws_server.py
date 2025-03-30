# websocket_server.py
import asyncio
import websockets
import json

# This will be our "bridge" where WebSocket messages are forwarded to Flask-SocketIO
websocket_clients = []

async def handle_websocket_connection(websocket):
    websocket_clients.append(websocket)
    try:
        async for message in websocket:
            # When a message is received from WebSocket client, process it
            print(f"Received message from WebSocket: {message}")

            # Example: You can send the message to Flask-SocketIO (use a mechanism like an event)
            for client in websocket_clients:
                await client.send(json.dumps({'status': 'message received', 'message': message}))
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    finally:
        websocket_clients.remove(websocket)

async def main():
    start_server = await websockets.serve(handle_websocket_connection, "localhost", 9090)
    print("WebSocket server started on ws://127.0.0.1:9090")
    await asyncio.Future()  # Run forever

asyncio.run(main())
