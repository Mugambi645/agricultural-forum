
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from location_field.models.plain import PlainLocationField 
class Discussion(models.Model):
    """Represents a main discussion post in the forum."""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discussions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    location = PlainLocationField(
        based_fields=['title'], # This field will be used to automatically set the map center
        zoom=10,                 # Zoom level for this specific map
        blank=True,              # Make it optional
        null=True                # Allow NULL in database
    )
    class Meta:
        ordering = ['-created_at'] # Order discussions by newest first

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a particular discussion instance."""
        return reverse('discussions:discussion_detail', args=[str(self.id)])

class Comment(models.Model):
    """Represents a comment on a discussion post."""
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_flagged = models.BooleanField(default=False) # For ML moderation
    flag_reason = models.TextField(blank=True, null=True) # Reason for flagging

    class Meta:
        ordering = ['created_at'] # Order comments by oldest first

    def __str__(self):
        return f"Comment by {self.author.username} on {self.discussion.title}"

class ContentAttachment(models.Model):
    """Allows users to attach images or files to discussions or comments."""
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments')
    file = models.FileField(upload_to='attachments/files/', blank=True, null=True)
    image = models.ImageField(upload_to='attachments/images/', blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.discussion:
            return f"Attachment for Discussion: {self.discussion.title}"
        elif self.comment:
            return f"Attachment for Comment: {self.comment.id}"
        return "Standalone Attachment"