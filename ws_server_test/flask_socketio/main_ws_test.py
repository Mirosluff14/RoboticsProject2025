# NOTE: Needs testing, also one extra requirement: pip install websocket-client

from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import json
import websocket
import asyncio
from picamera2 import Picamera2, Preview
from libcamera import Transform
import time
import cv2
import threading
import io
import queue
import os
from ultralytics import YOLO


######## Define the app and global parameters ########
ROSBRIDGE_WS = "ws://127.0.0.1:9090"  # Your ROS 2 IP address and port
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Streaming global flag
stream_video = False
# Dataset recording global flag
record_dataset = False
dataset_folder = "dataset"
# Check if dataset folder exists
if not os.path.exists(dataset_folder):
    os.makedirs(dataset_folder)
else:
    num_stored = len(os.listdir(dataset_folder))
    sample_index = num_stored - 1 if num_stored > 0 else 0

######## Camera functions ##########

# Initialize the camera
picam2 = Picamera2()

modes = picam2.sensor_modes
print(modes)

# Create a configuration for capturing at 640x480 resolution with short exposure mode
camera_config = picam2.create_video_configuration(main={"size": (1640, 1232),
                                                          "format": "RGB888"},
                                                    transform=Transform(vflip=True))
# Set short exposure mode
camera_config["controls"] = {"ExposureTime": 2000}  # Set exposure time in microseconds
# Configure the camera
picam2.configure(camera_config)

# Set the frame rate by manually setting the framerate via the `set_controls` method
#picam2.set_controls({"FrameRate": 30})
# Start the camera
picam2.start()

# Function to capture and save to dataset folder
def capture_and_save(action):
    global sample_index
    start_time = time.time()
    filepath = f"{dataset_folder}/{sample_index}_{action}.jpg" # FORMAT: index_action.jpg
    picam2.capture_file(filepath)
    end_time = time.time()
    print(f"Time taken: {end_time-start_time}")
    sample_index += 1


# Function to capture frames from the camera and emit them over WebSocket
def capture_and_stream():
    global stream_video
    while True:
        if stream_video:
            # Capture a frame from the camera
            data = io.BytesIO()
            picam2.capture_file(data, format='jpeg')
            data.seek(0)
            
            jpeg_bytes = data.read()

            # Emit the JPEG image over WebSocket
            socketio.emit('video_frame', {'frame': jpeg_bytes})

            # Sleep for a short time to maintain the frame rate
            socketio.sleep(1 / 30)  # 30 FPS



        else:
            # Sleep, no capturing required
            socketio.sleep(1)  # 30 FPS

# Start the capture and streaming thread
thread = threading.Thread(target=capture_and_stream)
thread.daemon = True
thread.start()

# Websocket client code:
# Queue for sending messages to WebSocket server
message_queue = queue.Queue()

class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.ws = None
        self.running = True

    def connect(self):
        """Connect to WebSocket server and listen for messages."""
        while self.running:
            try:
                self.ws = websocket.WebSocketApp(self.url,
                                                 on_message=self.on_message,
                                                 on_error=self.on_error,
                                                 on_close=self.on_close)
                self.ws.run_forever()
            except Exception as e:
                print(f"WebSocket connection error: {e}")
            time.sleep(2)  # Retry connection after a delay

    def on_message(self, ws, message):
        """Handle incoming messages from WebSocket server."""
        print(f"Received message from WebSocket server: {message}")
        #socketio.emit('new_message', {'data': message})  # Forward to frontend

    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed: ", close_status_code, close_msg)

    def send_message(self, message):
        """Send message through the persistent WebSocket connection."""
        if self.ws and self.ws.sock and self.ws.sock.connected:
            self.ws.send(message)
        else:
            print("WebSocket not connected, message not sent")

# Create WebSocket client instance for ROS bridge
ws_client = WebSocketClient(ROSBRIDGE_WS)

def websocket_thread():
    """Run WebSocket client in a separate thread."""
    ws_client.connect()

# Start WebSocket client in a separate thread
ws_thread = threading.Thread(target=websocket_thread, daemon=True)
ws_thread.start()

# Record switch handling
@socketio.on('turn_dataset_recording')
def handle_record_switch(data):
    global record_dataset
    record_dataset = data
    print(f"Dataset recording: {record_dataset}")

# Video stream handling
@socketio.on('toggle_video_stream')
def handle_stream_switch(data):
    global stream_video
    stream_video = data

# Message handling for ROS bridge
@socketio.on('manual_control_command')
def handle_manual_input(data):
    print(f"Received manual command: {data}")
    topic = "/motor_control"
    message_data = {"op": "publish", "topic": topic, "msg": {"data": data}}
    ws_client.send_message(json.dumps(message_data))
    if record_dataset:
        capture_and_save(data)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    # Set Flask to listen on all network interfaces (0.0.0.0)
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
