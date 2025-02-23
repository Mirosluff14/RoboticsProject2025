import asyncio
import websockets
import json

ROSBRIDGE_WS = "ws://192.168.1.109:9090"

async def send_ros_message():
    async with websockets.connect(ROSBRIDGE_WS) as websocket:
        # Define the ROS 2 message type and topic
        topic_advertise = {
            "op": "advertise",
            "topic": "/test_topic",
            "type": "std_msgs/String"
        }
        await websocket.send(json.dumps(topic_advertise))
        print("Topic advertised.")

        # Send a message to the topic
        message_data = {
            "op": "publish",
            "topic": "/test_topic",
            "msg": {"data": "Hello from Python WebSocket!"}
        }
        await websocket.send(json.dumps(message_data))
        print("Message sent.")

        # Subscribe to the topic
        topic_subscribe = {
            "op": "subscribe",
            "topic": "/test_topic"
        }
        await websocket.send(json.dumps(topic_subscribe))
        print("Subscribed to topic.")

        # Listen for incoming messages
        while True:
            response = await websocket.recv()
            print("Received:", response)

asyncio.run(send_ros_message())