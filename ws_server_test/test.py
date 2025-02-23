import asyncio
import websockets
import json
import keyboard
import time

ROSBRIDGE_WS = "ws://192.168.1.109:9090"  # put your ROS 2 IP address here after ws://, port 9090

async def send_ros_message():
    async with websockets.connect(ROSBRIDGE_WS) as websocket:
        # Listen for keyboard events
        counter = 0
        while True:
            time.sleep(0.1)
            if keyboard.is_pressed('w'):
                message_data = {"op": "publish", "topic": "/motor_control", "msg": {"data": 1}}
                await websocket.send(json.dumps(message_data))
                print("Sent message: 1")
            elif keyboard.is_pressed('s'):
                message_data = {"op": "publish", "topic": "/motor_control", "msg": {"data": 2}}
                await websocket.send(json.dumps(message_data))
                print("Sent message: 2")
            elif keyboard.is_pressed('f'):
                message_data = {"op": "publish", "topic": "/motor_control", "msg": {"data": 3}}
                await websocket.send(json.dumps(message_data))
                print("Sent message: 3")
            elif keyboard.is_pressed('a'):
                message_data = {"op": "publish", "topic": "/motor_control", "msg": {"data": 4}}
                await websocket.send(json.dumps(message_data))
                print("Sent message: 4")
            elif keyboard.is_pressed('d'):
                message_data = {"op": "publish", "topic": "/motor_control", "msg": {"data": 5}}
                await websocket.send(json.dumps(message_data))
                print("Sent message: 5")
            elif counter > 10:
                counter = 0
                message_data = {"op": "publish", "topic": "/motor_control", "msg": {"data": 3}}
                await websocket.send(json.dumps(message_data))
                print("Sent message: 3")
            else:
                counter += 1

            # Check for incoming messages from the websocket
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                print("Received:", response)
            except asyncio.TimeoutError:
                pass

asyncio.run(send_ros_message())