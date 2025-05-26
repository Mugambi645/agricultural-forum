
from django import forms
from .models import DiseasePrediction

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = DiseasePrediction
        fields = ['image']
        labels = {
            'image': 'Upload Plant Image',
        }
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }