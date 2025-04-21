from flask import Flask, Response
from picamera2 import Picamera2, Preview
from libcamera import Transform
import cv2
import time

app = Flask(__name__)

# Initialize camera
picam2 = Picamera2()

camera_config = picam2.create_video_configuration(
    main={"size": (1640, 922), "format": "RGB888"},
    buffer_count=1,
    transform=Transform(vflip=True, hflip=True)
)
picam2.configure(camera_config)
picam2.set_controls({"FrameRate": 30})
picam2.start()

@app.route('/video_feed')
def video_feed():
    def generate_frames():
        while True:
            frame = picam2.capture_array()
            resized_frame = cv2.resize(frame, (640, 360), interpolation=cv2.INTER_LINEAR)
            _, buffer = cv2.imencode('.jpg', resized_frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(1/30)
            #print("Frame sent")

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
