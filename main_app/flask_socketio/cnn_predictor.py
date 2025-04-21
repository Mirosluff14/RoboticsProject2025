import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

# Action dictionary

class SimpleCNN(nn.Module):
    def __init__(self, num_classes=5):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(32 * 56 * 56, 512)
        self.fc2 = nn.Linear(512, num_classes)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 32 * 56 * 56)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Define a custom function to load the model
class ActionPredictor():
    def __init__(self, model_path, num_classes=5):
        self.model = SimpleCNN(num_classes=num_classes)
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        self.model.eval()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self.actions = {
            0: "Forward",
            1: "Backward",
            2: "Stop",
            3: "Left",
            4: "Right"
        }
    
    def predict(self, image):
        # Convert the image to a PyTorch tensor
        # Assuming image is a numpy array or PIL Image
        # Convert the image to a PIL Image if it's a numpy array
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        image = self.transform(image).unsqueeze(0)
        with torch.no_grad():
            output = self.model(image)
            _, predicted = torch.max(output, 1)
        # Get the action name from the dictionary
        action_name = self.actions[predicted.item()]
        return action_name
