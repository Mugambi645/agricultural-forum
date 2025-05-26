# discussions/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F

from .models import Discussion, Comment, ContentAttachment
from .forms import DiscussionCreateForm, CommentCreateForm

import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.contrib import messages # Import for user feedback

# --- ML Model Placeholder ---
def predict_irregular_comment(comment_text):
    comment_text_lower = comment_text.lower()
    if "badword" in comment_text_lower or "spam" in comment_text_lower:
        return True, "Contains flagged keywords"
    return False, None

# --- Views ---

def discussion_list(request):
    discussions = Discussion.objects.all()
    return render(request, 'discussions/discussion_list.html', {'discussions': discussions})

def discussion_detail(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)
    comments = Comment.objects.filter(discussion=discussion, parent=None, is_deleted=False).order_by('-votes', '-created_at')
    
    # CORRECTED: Use .attachments.all() as per related_name in models.py
    attachments = discussion.attachments.all() 

    comment_form = CommentCreateForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.info(request, "You need to be logged in to post comments.")
            return redirect('accounts:login')

        comment_form = CommentCreateForm(request.POST, request.FILES)
        if comment_form.is_valid():
            with transaction.atomic():
                new_comment = comment_form.save(commit=False)
                new_comment.discussion = discussion
                new_comment.author = request.user

                parent_id = comment_form.cleaned_data.get('parent')
                if parent_id:
                    new_comment.parent = get_object_or_404(Comment, pk=parent_id, is_deleted=False)

                is_flagged, flag_reason = predict_irregular_comment(new_comment.content)
                new_comment.is_flagged = is_flagged
                new_comment.flag_reason = flag_reason
                new_comment.save()

                attachment_file = request.FILES.get('attachment_file')
                attachment_image = request.FILES.get('attachment_image')
                attachment_description = comment_form.cleaned_data.get('attachment_description', '')

                if attachment_file:
                    ContentAttachment.objects.create(
                        comment=new_comment,
                        file=attachment_file,
                        description=attachment_description
                    )
                if attachment_image:
                    ContentAttachment.objects.create(
                        comment=new_comment,
                        image=attachment_image,
                        description=attachment_description
                    )

                attachments_data = []
                # Already correct here: new_comment.attachments.all()
                for attachment in new_comment.attachments.all():
                    attachments_data.append({
                        'file_url': attachment.file.url if attachment.file else None,
                        'image_url': attachment.image.url if attachment.image else None,
                        'description': attachment.description
                    })

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'discussion_{pk}',
                    {
                        'type': 'new_comment_notification',
                        'message': {
                            'id': new_comment.id,
                            'author': new_comment.author.username,
                            'author_id': new_comment.author.id,
                            'content': new_comment.content,
                            'created_at': new_comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                            'is_flagged': new_comment.is_flagged,
                            'flag_reason': new_comment.flag_reason,
                            'votes': new_comment.votes,
                            'parent_id': new_comment.parent.id if new_comment.parent else None,
                            'attachments': attachments_data
                        }
                    }
                )

                messages.success(request, "Your comment has been posted successfully!")
                return redirect('discussions:discussion_detail', pk=pk)

    context = {
        'discussion': discussion,
        'comments': comments,
        'attachments': attachments, # This now correctly refers to discussion.attachments.all()
        'comment_form': comment_form,
    }
    return render(request, 'discussions/discussion_detail.html', context)

@login_required
def create_discussion(request):
    form = DiscussionCreateForm()
    if request.method == 'POST':
        form = DiscussionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                discussion = form.save(commit=False)
                discussion.author = request.user
                discussion.save()

                attachment_file = request.FILES.get('attachment_file')
                attachment_image = request.FILES.get('attachment_image')
                attachment_description = form.cleaned_data.get('attachment_description', '')

                if attachment_file:
                    ContentAttachment.objects.create(
                        discussion=discussion,
                        file=attachment_file,
                        description=attachment_description
                    )
                if attachment_image:
                    ContentAttachment.objects.create(
                        discussion=discussion,
                        image=attachment_image,
                        description=attachment_description
                    )
                messages.success(request, "Your discussion has been created successfully!")
                return redirect('discussions:discussion_detail', pk=discussion.pk)
    return render(request, 'discussions/create_discussion.html', {'form': form})

@login_required
def upvote_comment(request, pk):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, pk=pk)
        Comment.objects.filter(pk=pk).update(votes=F('votes') + 1)
        comment.refresh_from_db()
        return JsonResponse({'status': 'success', 'votes': comment.votes})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def downvote_comment(request, pk):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, pk=pk)
        Comment.objects.filter(pk=pk).update(votes=F('votes') - 1)
        comment.refresh_from_db()
        return JsonResponse({'status': 'success', 'votes': comment.votes})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user == comment.author:
        comment.is_deleted = True
        comment.content = "[This comment has been deleted]"
        comment.save()
        messages.success(request, "Comment successfully deleted.")
    else:
        messages.error(request, "You are not authorized to delete this comment.")
    return redirect('discussions:discussion_detail', pk=comment.discussion.pk)

@login_required
def reply_to_comment(request, discussion_pk, parent_pk):
    discussion = get_object_or_404(Discussion, pk=discussion_pk)
    parent_comment = get_object_or_404(Comment, pk=parent_pk, is_deleted=False)

    if request.method == 'POST':
        form = CommentCreateForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                new_comment = form.save(commit=False)
                new_comment.discussion = discussion
                new_comment.author = request.user
                new_comment.parent = parent_comment

                is_flagged, flag_reason = predict_irregular_comment(new_comment.content)
                new_comment.is_flagged = is_flagged
                new_comment.flag_reason = flag_reason
                new_comment.save()

                attachment_file = request.FILES.get('attachment_file')
                attachment_image = request.FILES.get('attachment_image')
                attachment_description = form.cleaned_data.get('attachment_description', '')

                if attachment_file:
                    ContentAttachment.objects.create(
                        comment=new_comment,
                        file=attachment_file,
                        description=attachment_description
                    )
                if attachment_image:
                    ContentAttachment.objects.create(
                        comment=new_comment,
                        image=attachment_image,
                        description=attachment_description
                    )

                attachments_data = []
                # Already correct here: new_comment.attachments.all()
                for attachment in new_comment.attachments.all():
                    attachments_data.append({
                        'file_url': attachment.file.url if attachment.file else None,
                        'image_url': attachment.image.url if attachment.image else None,
                        'description': attachment.description
                    })

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'discussion_{discussion_pk}',
                    {
                        'type': 'new_comment_notification',
                        'message': {
                            'id': new_comment.id,
                            'author': new_comment.author.username,
                            'author_id': new_comment.author.id,
                            'content': new_comment.content,
                            'created_at': new_comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                            'is_flagged': new_comment.is_flagged,
                            'flag_reason': new_comment.flag_reason,
                            'votes': new_comment.votes,
                            'parent_id': new_comment.parent.id if new_comment.parent else None,
                            'attachments': attachments_data
                        }
                    }
                )

                messages.success(request, "Your reply has been posted successfully!")
                return redirect('discussions:discussion_detail', pk=discussion_pk)
    else:
        form = CommentCreateForm(initial={'parent': parent_pk})

    context = {
        'form': form,
        'discussion': discussion,
        'parent_comment': parent_comment,
    }
    return render(request, 'discussions/reply_comment.html', context)