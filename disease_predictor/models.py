
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
class DiseasePrediction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='disease_predictions')
    image = models.ImageField(upload_to='disease_images/')
    prediction_label = models.CharField(max_length=100, blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)
    predicted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.prediction_label} ({self.confidence:.2f}) by {self.user.username if self.user else 'Anonymous'}"

    class Meta:
        ordering = ['-predicted_at']