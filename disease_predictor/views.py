
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os

from .forms import ImageUploadForm
from .models import DiseasePrediction

# Import your dummy disease predictor
from ml_model.disease_predictor import predict_disease

# You can add a message framework for user feedback
from django.contrib import messages

@login_required # Only logged-in users can use the detector
def disease_detector_view(request):
    prediction_result = None
    uploaded_image_url = None

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded image to MEDIA_ROOT
            prediction_instance = form.save(commit=False)
            prediction_instance.user = request.user
            prediction_instance.save() # This saves the image file to disk

            uploaded_image_url = prediction_instance.image.url
            image_path = prediction_instance.image.path # Get the absolute path to the saved image

            # Perform prediction using the PyTorch model
            predicted_label, confidence = predict_disease(image_path)

            # Update the prediction instance with results
            prediction_instance.prediction_label = predicted_label
            prediction_instance.confidence = confidence
            prediction_instance.save()

            prediction_result = prediction_instance
            messages.success(request, "Image uploaded and processed successfully!")
        else:
            messages.error(request, "Error uploading image. Please check the file type.")
    else:
        form = ImageUploadForm()

    # Get recent predictions for the current user
    recent_predictions = DiseasePrediction.objects.filter(user=request.user).order_by('-predicted_at')[:5]

    context = {
        'form': form,
        'prediction_result': prediction_result,
        'uploaded_image_url': uploaded_image_url,
        'recent_predictions': recent_predictions,
    }
    return render(request, 'disease_detector/detector.html', context)