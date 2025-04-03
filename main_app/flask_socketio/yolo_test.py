from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import json
import websockets
import asyncio
from picamera2 import Picamera2, Preview
from libcamera import Transform
import time
import cv2
import threading
import io
from ultralytics import YOLO

ROSBRIDGE_WS = "ws://127.0.0.1:9090"  # Your ROS 2 IP address and port

app = Flask(__name__)
socketio = SocketIO(app)


# Initialize the camera
picam2 = Picamera2()

modes = picam2.sensor_modes
print(modes)

# Create a configuration for capturing at 640x480 resolution
camera_config = picam2.create_preview_configuration(main={"size": (1280, 720)}, transform=Transform(vflip=True))

# Configure the camera
picam2.configure(camera_config)


# Set the frame rate by manually setting the framerate via the `set_controls` method
#picam2.set_controls({"FrameRate": 30})

# Start the camera
picam2.start()

# Load the exported NCNN model
ncnn_model = YOLO("yolo11n_ncnn_model")

# Function to capture frames from the camera and emit them over WebSocket
def capture_and_stream():
    while True:
    # Capture frame-by-frame
        frame = picam2.capture_array()

        # Run YOLO11 inference on the frame
        results = ncnn_model(frame)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()
        
        ret, jpeg_frame = cv2.imencode('.jpg', annotated_frame)

        if ret:
            # Emit the JPEG image over WebSocket
            socketio.emit('video_frame', {'frame': jpeg_frame.tobytes()})

        # Sleep for a short time to maintain the frame rate
        time.sleep(1 / 60)  # 30 FPS

# Start the capture and streaming thread
thread = threading.Thread(target=capture_and_stream)
thread.daemon = True
thread.start()


async def send_ros_message_to_rosbridge(message_data):
    async with websockets.connect(ROSBRIDGE_WS) as websocket:
        await websocket.send(json.dumps(message_data))
        response = await websocket.recv()
        print("Received response from ROS bridge:", response)

@socketio.on('keyboard_input')
def handle_keyboard_input(data):
    print(f"Received keyboard input: {data}")
    message_data = {"op": "publish", "topic": "/motor_control", "msg": {"data": data}}
    asyncio.run(send_ros_message_to_rosbridge(message_data))

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    # Set Flask to listen on all network interfaces (0.0.0.0)
    socketio.run(app, host='0.0.0.0', port=5000)
