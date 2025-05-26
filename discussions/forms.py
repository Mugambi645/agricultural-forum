
from django import forms
from .models import Discussion, Comment, ContentAttachment
from location_field.forms.plain import PlainLocationField as LocationFormField 
class DiscussionForm(forms.ModelForm):
    """Form for creating a new discussion post."""
    class Meta:
        model = Discussion
        fields = ['title', 'content'] # Author will be set automatically

class CommentForm(forms.ModelForm):
    """Form for adding a comment to a discussion."""
    class Meta:
        model = Comment
        fields = ['content'] # Discussion and author will be set automatically

class ContentAttachmentForm(forms.ModelForm):
    """Form for uploading files/images."""
    class Meta:
        model = ContentAttachment
        fields = ['file', 'image', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Optional description for your attachment'}),
        }

class DiscussionCreateForm(forms.ModelForm):
    attachment_file = forms.FileField(required=False, label="Upload File")
    attachment_image = forms.ImageField(required=False, label="Upload Image")
    attachment_description = forms.CharField(max_length=255, required=False, label="Attachment Description")

    # Add location field to the form
    location = LocationFormField(
        required=False,
        label="Location on Map"
    )

    class Meta:
        model = Discussion
        fields = ['title', 'content', 'location'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure the location field instance is correctly assigned
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['location'].initial = kwargs['instance'].location

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Manually save the location field data if not handled by crispy
        if 'location' in self.cleaned_data:
            instance.location = self.cleaned_data['location']
        if commit:
            instance.save()
        return instance


class CommentCreateForm(forms.ModelForm):
    """Combined form for creating a comment with optional attachments."""
    attachment_file = forms.FileField(required=False, label="Upload File")
    attachment_image = forms.ImageField(required=False, label="Upload Image")
    attachment_description = forms.CharField(max_length=255, required=False, label="Attachment Description")
    #parent = forms.IntegerField(widget=forms.HiddenInput, required=False) 
    class Meta:
        model = Comment
        fields = ['content', 'parent'] # Keep 'parent' here, as it refers to the model field
        widgets = {
            # ADD this widget to make the 'parent' field hidden
            'parent': forms.HiddenInput(),
        }