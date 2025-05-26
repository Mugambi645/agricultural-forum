
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction # For atomic operations
from .models import Discussion, Comment, ContentAttachment
from .forms import DiscussionCreateForm, CommentCreateForm
import json # For sending JSON data via Channels
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import os # For ML model path

# --- ML Model Placeholder ---
# In a real application, you would load your trained ML model here.
# For demonstration, we'll use a simple dummy function.
# You might want to put this in a separate 'ml_model' app/directory.

# Dummy ML model for flagging comments
def predict_irregular_comment(comment_text):
    """
    This is a placeholder for your machine learning model.
    In a real scenario, you would load a trained model (e.g., scikit-learn, TensorFlow, PyTorch)
    and use it to classify the comment text.

    For demonstration, we'll just flag comments containing "badword" or "spam".
    """
    comment_text_lower = comment_text.lower()
    if "badword" in comment_text_lower or "spam" in comment_text_lower:
        return True, "Contains flagged keywords"
    return False, None

# --- Views ---

def discussion_list(request):
    """Displays a list of all discussions."""
    discussions = Discussion.objects.all()
    return render(request, 'discussions/discussion_list.html', {'discussions': discussions})

def discussion_detail(request, pk):
    """Displays a single discussion and its comments, with a form to add new comments."""
    discussion = get_object_or_404(Discussion, pk=pk)
    comments = discussion.comments.all()
    attachments = discussion.attachments.all()
    comment_form = CommentCreateForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('accounts:login') # Redirect to login if not authenticated

        comment_form = CommentCreateForm(request.POST, request.FILES)
        if comment_form.is_valid():
            with transaction.atomic(): # Ensure atomicity for comment and attachment
                new_comment = comment_form.save(commit=False)
                new_comment.discussion = discussion
                new_comment.author = request.user

                # --- ML Moderation ---
                is_flagged, flag_reason = predict_irregular_comment(new_comment.content)
                new_comment.is_flagged = is_flagged
                new_comment.flag_reason = flag_reason
                # You might add logic here to prevent saving if flagged severely,
                # or require admin approval. For now, we just flag it.
                # --- End ML Moderation ---

                new_comment.save()

                # Handle attachments for the comment
                if comment_form.cleaned_data['attachment_file']:
                    ContentAttachment.objects.create(
                        comment=new_comment,
                        file=comment_form.cleaned_data['attachment_file'],
                        description=comment_form.cleaned_data['attachment_description']
                    )
                if comment_form.cleaned_data['attachment_image']:
                    ContentAttachment.objects.create(
                        comment=new_comment,
                        image=comment_form.cleaned_data['attachment_image'],
                        description=comment_form.cleaned_data['attachment_description']
                    )

                # --- Real-time: Send new comment to WebSocket ---
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'discussion_{pk}', # Group name for this discussion
                    {
                        'type': 'new_comment_notification', # Corresponds to a method in consumer
                        'message': {
                            'id': new_comment.id,
                            'author': new_comment.author.username,
                            'content': new_comment.content,
                            'created_at': new_comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                            'is_flagged': new_comment.is_flagged,
                            'flag_reason': new_comment.flag_reason,
                            'attachments': [
                                {
                                    'file_url': attachment.file.url if attachment.file else None,
                                    'image_url': attachment.image.url if attachment.image else None,
                                    'description': attachment.description
                                } for attachment in new_comment.attachments.all()
                            ]
                        }
                    }
                )
                # --- End Real-time ---

                return redirect('discussions:discussion_detail', pk=pk) # Redirect to prevent form resubmission

    context = {
        'discussion': discussion,
        'comments': comments,
        'attachments': attachments,
        'comment_form': comment_form,
    }
    return render(request, 'discussions/discussion_detail.html', context)

@login_required
def create_discussion(request):
    """Allows authenticated users to create a new discussion post."""
    form = DiscussionCreateForm()
    if request.method == 'POST':
        form = DiscussionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                discussion = form.save(commit=False)
                discussion.author = request.user
                discussion.save()

                # Handle attachments for the discussion
                if form.cleaned_data['attachment_file']:
                    ContentAttachment.objects.create(
                        discussion=discussion,
                        file=form.cleaned_data['attachment_file'],
                        description=form.cleaned_data['attachment_description']
                    )
                if form.cleaned_data['attachment_image']:
                    ContentAttachment.objects.create(
                        discussion=discussion,
                        image=form.cleaned_data['attachment_image'],
                        description=form.cleaned_data['attachment_description']
                    )
                return redirect('discussions:discussion_detail', pk=discussion.pk)
    return render(request, 'discussions/create_discussion.html', {'form': form})