
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import json
import os # Ensure os is imported for path handling

# Determine the base directory for model artifacts (relative to this script)
# This handles both development and deployment paths robustly.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load class labels and their details from the enhanced JSON file
try:
    with open(os.path.join(BASE_DIR, 'class_names.json')) as f:
        # Load as a list of dictionaries
        CLASS_DETAILS = json.load(f)
    # Create a mapping from model's internal class name to its full details
    CLASS_NAME_MAP = {item['name']: item for item in CLASS_DETAILS}
    # Get the ordered list of names that the model will predict
    # This assumes your JSON is ordered correctly, or you sort it if needed
    CLASS_NAMES_ORDERED = [item['name'] for item in CLASS_DETAILS]
except FileNotFoundError:
    print("Error: class_names.json not found. Make sure it's in the 'model' directory.")
    # Fallback or raise error, depending on desired behavior
    CLASS_DETAILS = []
    CLASS_NAME_MAP = {}
    CLASS_NAMES_ORDERED = []
except json.JSONDecodeError:
    print("Error: class_names.json is not valid JSON.")
    CLASS_DETAILS = []
    CLASS_NAME_MAP = {}
    CLASS_NAMES_ORDERED = []


# Load model
_model = None # Use global variable to load model once
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = os.path.join(BASE_DIR, 'plant_disease_model.pth')

def load_model():
    global _model
    if _model is None:
        print(f"Loading PyTorch model on {_device} for inference...")
        model_local = models.resnet18(weights=None) # No pretrained weights at init
        num_classes = len(CLASS_NAMES_ORDERED)
        model_local.fc = nn.Linear(model_local.fc.in_features, num_classes)

        if os.path.exists(MODEL_PATH):
            try:
                model_local.load_state_dict(torch.load(MODEL_PATH, map_location=_device))
                print(f"Model loaded successfully from {MODEL_PATH}")
            except Exception as e:
                print(f"Error loading model weights from {MODEL_PATH}: {e}")
                print("Using randomly initialized weights, predictions will be unreliable.")
        else:
            print(f"WARNING: Model file not found at {MODEL_PATH}. Using randomly initialized weights.")
            print("Ensure 'plant_disease_model.pth' is in the 'model' directory.")

        model_local.eval() # Set model to evaluation mode
        _model = model_local.to(_device) # Move model to device
    return _model

# Define transform (matches training validation transform)
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

def predict_image(image_path):
    model_instance = load_model() # Ensure model is loaded

    try:
        image = Image.open(image_path).convert('RGB')
        img_t = transform(image)
        batch_t = torch.unsqueeze(img_t, 0).to(_device) # Move input to device

        with torch.no_grad():
            out = model_instance(batch_t)
            probabilities = torch.nn.functional.softmax(out, dim=1)[0] # Get probabilities
            confidence, index = torch.max(probabilities, 0) # Get max confidence and its index

        # Retrieve full details using the predicted index
        predicted_name_raw = CLASS_NAMES_ORDERED[index.item()]
        predicted_details = CLASS_NAME_MAP.get(predicted_name_raw, {
            "name": predicted_name_raw,
            "common_name": "Unknown",
            "description": "No detailed information available for this prediction.",
            "remedy": "Consult a plant expert.",
            "is_healthy": False
        })

        return {
            "class_name_raw": predicted_name_raw, # Original model output
            "common_name": predicted_details.get("common_name"),
            "confidence": confidence.item() * 100, # Convert to percentage
            "description": predicted_details.get("description"),
            "remedy": predicted_details.get("remedy"),
            "is_healthy": predicted_details.get("is_healthy")
        }
    except FileNotFoundError:
        return {"error": "Image file not found."}
    except Exception as e:
        return {"error": f"Prediction failed: {e}"}


