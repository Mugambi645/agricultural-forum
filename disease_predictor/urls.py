# disease_detector/urls.py
from django.urls import path
from . import views
app_name = "disease_predictor"
urlpatterns = [
    path('', views.disease_detector_view, name='disease_detector'),
]