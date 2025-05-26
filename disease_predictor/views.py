# --- Now, in your disease_detector/views.py (which uses the above module) ---
# Assuming you place the model loading logic in a separate file (e.g., ml_model/disease_predictor.py)
# and then import predict_image from there.

from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings # Import settings to get MEDIA_ROOT
import os
from .forms import ImageUploadForm # Assuming you use the form defined earlier
from .models import DiseasePrediction # Assuming you have a model to store predictions

# Import the prediction function from your ml_model module
# (Adjust this import path based on where you put the above code)
from model.disease_predictor import predict_image, load_model # Also load_model to ensure it runs on startup

# Ensure the model is loaded when Django starts (best practice)
load_model()


def predict_view(request):
    prediction_result = None
    uploaded_image_url = None
    form = ImageUploadForm() # Initialize form for GET request

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            prediction_instance = form.save(commit=False)
            prediction_instance.user = request.user if request.user.is_authenticated else None
            prediction_instance.save() # Saves the image file to MEDIA_ROOT

            uploaded_image_url = prediction_instance.image.url
            full_image_path = prediction_instance.image.path # Get absolute path to the saved image

            # Call the improved predict_image function
            prediction_data = predict_image(full_image_path)

            if "error" in prediction_data:
                # Handle prediction errors gracefully
                prediction_result = {"error": prediction_data["error"]}
                # You might want to save error status to DiseasePrediction model as well
            else:
                # Store prediction details back to the database model
                prediction_instance.prediction_label = prediction_data["common_name"]
                prediction_instance.confidence = prediction_data["confidence"]
                # Add more fields to your DiseasePrediction model if you want to save description/remedy
                # prediction_instance.description = prediction_data["description"]
                # prediction_instance.remedy = prediction_data["remedy"]
                prediction_instance.save()

                prediction_result = {
                    "common_name": prediction_data["common_name"],
                    "confidence": prediction_data["confidence"],
                    "description": prediction_data["description"],
                    "remedy": prediction_data["remedy"],
                    "is_healthy": prediction_data["is_healthy"]
                }
        else:
            prediction_result = {"error": "Invalid form submission. Please check the image file."}

    context = {
        'form': form,
        'prediction': prediction_result, # Changed variable name to 'prediction' for clarity in template
        'uploaded_image_url': uploaded_image_url,
    }
    return render(request, 'disease_predictor/predict.html', context) # Adjusted template path