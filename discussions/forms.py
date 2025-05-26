
from django import forms
from .models import Discussion, Comment, ContentAttachment

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

# You might want to combine these for a single upload interface
class DiscussionCreateForm(forms.ModelForm):
    """Combined form for creating a discussion with optional attachments."""
    attachment_file = forms.FileField(required=False, label="Upload File")
    attachment_image = forms.ImageField(required=False, label="Upload Image")
    attachment_description = forms.CharField(max_length=255, required=False, label="Attachment Description")

    class Meta:
        model = Discussion
        fields = ['title', 'content']

class CommentCreateForm(forms.ModelForm):
    """Combined form for creating a comment with optional attachments."""
    attachment_file = forms.FileField(required=False, label="Upload File")
    attachment_image = forms.ImageField(required=False, label="Upload Image")
    attachment_description = forms.CharField(max_length=255, required=False, label="Attachment Description")

    class Meta:
        model = Comment
        fields = ['content']