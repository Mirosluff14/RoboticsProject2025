from picamera2 import Picamera2, Preview
from libcamera import Transform
from ultralytics import YOLO
import cv2
import time
import os

# Set the current working directory to the file's location
current_dir = os.path.dirname(os.path.abspath(__file__))
print(current_dir)

save_location = current_dir + "images"

# Initialize the camera
picam2 = Picamera2()

modes = picam2.sensor_modes
print(modes)

# Create a configuration for capturing at 640x480 resolution with short exposure mode
camera_config = picam2.create_video_configuration(main={"size": (1640, 922),
                                                          "format": "RGB888"},
                                                    transform=Transform(vflip=True))
# Set short exposure mode
#camera_config["controls"] = {"ExposureTime": 5000}  # Set exposure time in microseconds
# Configure the camera
picam2.configure(camera_config)
picam2.start()

# Load the exported NCNN model
ncnn_model = YOLO("best.torchscript", task=None)

# Function to capture frames from the camera and emit them over WebSocket

for i in range(5):
    # Capture frame-by-frame
    frame = picam2.capture_array()

    # Run YOLO11 inference on the frame
    results = ncnn_model(frame, workers=4)

    # Visualize the results on the frame
    annotated_frame = results[0].plot()
    
    # Save the annotated frame as a JPEG image
    timestamp = int(time.time())
    filename = f"frame_{timestamp}.jpg"
    cv2.imwrite(filename, annotated_frame)
    time.sleep(1)
