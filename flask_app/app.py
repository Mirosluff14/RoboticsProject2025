from flask import Flask, render_template, Response, request, jsonify
from flask_socketio import SocketIO, emit
import json
import websockets
import asyncio
import cv2
import threading

# ROS 2 rosbridge address
ROSBRIDGE_WS = "ws://127.0.0.1:9090"  

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize camera (use laptop webcam or external USB camera)
camera = cv2.VideoCapture(0)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

async def send_ros_message_to_rosbridge(message_data):
    async with websockets.connect(ROSBRIDGE_WS) as websocket:
        await websocket.send(json.dumps(message_data))
        response = await websocket.recv()
        print("Received response from ROS bridge:", response)

async def register_topic_if_not_exists(topic):
    async with websockets.connect(ROSBRIDGE_WS) as websocket:
        registration_message = {
            "op": "advertise",
            "topic": topic,
            "type": "std_msgs/String"
        }
        await websocket.send(json.dumps(registration_message))
        response = await websocket.recv()
        print("Topic registration response:", response)

@app.route('/control', methods=['POST'])
def control():
    data = request.json
    command = data.get("command")
    topic = "/motor_control"

    if command in ["FORWARD", "BACKWARD", "LEFT", "RIGHT", "STOP"]:
        message_data = {"op": "publish", "topic": topic, "msg": {"data": command}}
        asyncio.run(register_topic_if_not_exists(topic))
        asyncio.run(send_ros_message_to_rosbridge(message_data))
        return jsonify({"status": "sent", "command": command})
    else:
        return jsonify({"status": "error", "message": "Invalid Command"}), 400

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=1000)
