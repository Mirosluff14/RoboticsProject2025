import torch
from ultralytics.engine import exporter
import cv2

# reload our just trained model
#model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt')  # or yolov5n - yolov5x6, custom
model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.onnx', skip_validation=True)
print(model)
#torch.compile(model)
#model.eval()
#model.export()

image = "bus.jpg"
# Load and resize the image
img = cv2.imread(image)
img = cv2.resize(img, (640, 640))

for i in range(10):
    results = model(img)
    print(results.detections)