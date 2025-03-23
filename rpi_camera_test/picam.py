from picamera2 import Picamera2, Preview
from libcamera import Transform
import time

# Initialize the camera
picam2 = Picamera2()

modes = picam2.sensor_modes
print(modes)

# Create a configuration for capturing at 640x480 resolution
camera_config = picam2.create_preview_configuration(main={"size": (1280, 720)}, transform=Transform(vflip=True))

# Configure the camera
picam2.configure(camera_config)

# Start the camera preview (optional, you can remove this if you don't need preview)
picam2.start_preview(Preview.QTGL)

# Set the frame rate by manually setting the framerate via the `set_controls` method
picam2.set_controls({"FrameRate": 30})

# Start the camera
picam2.start()

# Wait for a moment to let the camera start
time.sleep(10)



# Capture an image and save it as 'test.jpg'
picam2.capture_file("test.jpg")
