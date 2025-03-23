from picamera2 import Picamera2, Preview
from libcamera import Transform
from ultralytics import YOLO


# Initialize the camera
picam2 = Picamera2()

modes = picam2.sensor_modes
print(modes)

picam2.preview_configuration.main.size = (1280, 720)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

# Load the exported NCNN model
ncnn_model = YOLO("yolo11n_ncnn_model")

# Function to capture frames from the camera and emit them over WebSocket

while True:
    # Capture frame-by-frame
    frame = picam2.capture_array()

    # Run YOLO11 inference on the frame
    results = ncnn_model(frame, workers=16)

    # Visualize the results on the frame
    annotated_frame = results[0].plot()