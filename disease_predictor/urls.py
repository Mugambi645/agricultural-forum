
from django.urls import path
from . import views
app_name = "disease_predictor"


urlpatterns = [
    path('', views.predict_view, name='predict'),
]