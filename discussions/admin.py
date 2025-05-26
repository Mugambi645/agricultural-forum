
from django.contrib import admin
from .models import Discussion, Comment, ContentAttachment

# ----------------------------------------------------
# 1. Customizing Discussion Admin
# ----------------------------------------------------
class ContentAttachmentInline(admin.TabularInline):
    """
    Allows managing attachments directly from the Discussion/Comment admin page.
    """
    model = ContentAttachment
    extra = 1 # Number of empty forms to display

@admin.register(Discussion) # This decorator is equivalent to admin.site.register(Discussion, DiscussionAdmin)
class DiscussionAdmin(admin.ModelAdmin):
    """
    Customizes the display and interaction for the Discussion model in the admin.
    """
    list_display = ('title', 'author', 'created_at', 'updated_at') # Fields to display in the list view
    list_filter = ('created_at', 'author') # Fields to filter by
    search_fields = ('title', 'content', 'author__username') # Fields to search across
    raw_id_fields = ('author',) # Use a raw ID input for ForeignKey for large user bases
    date_hierarchy = 'created_at' # Add a date drill-down navigation
    ordering = ('-created_at',) # Default ordering for the list

    # Add inlines to allow managing attachments from the Discussion detail page
    inlines = [ContentAttachmentInline]

    # Fieldsets for better organization in the detail view
    fieldsets = (
        (None, {
            'fields': ('title', 'content')
        }),
        ('Metadata', {
            'fields': ('author',),
            'classes': ('collapse',), # Makes this section collapsible
        }),
    )

# ----------------------------------------------------
# 2. Customizing Comment Admin
# ----------------------------------------------------
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Customizes the display and interaction for the Comment model in the admin.
    Highlights flagged comments.
    """
    list_display = ('content', 'discussion', 'author', 'created_at', 'is_flagged')
    list_filter = ('created_at', 'author', 'is_flagged')
    search_fields = ('content', 'author__username', 'discussion__title')
    raw_id_fields = ('discussion', 'author')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    # Display specific fields for flagged comments
    # You can make 'flag_reason' editable only if 'is_flagged' is True
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and not obj.is_flagged:
            # If not flagged, make flag_reason read-only or hide it
            # For simplicity, we'll just not show it in the form fieldsets if not flagged
            pass # Keep it in the fields list, but it will be empty
        return form

    fieldsets = (
        (None, {
            'fields': ('discussion', 'author', 'content')
        }),
        ('Moderation Status', {
            'fields': ('is_flagged', 'flag_reason'),
            'classes': ('collapse',),
            'description': 'AI-moderated flagging status. Flagged comments might require review.'
        }),
    )

    # Add custom actions for moderation (e.g., manually unflag a comment)
    actions = ['unflag_comments']

    def unflag_comments(self, request, queryset):
        """Action to manually unflag selected comments."""
        updated_count = queryset.update(is_flagged=False, flag_reason=None)
        self.message_user(request, f'{updated_count} comments successfully unflagged.', level=admin.messages.SUCCESS)
    unflag_comments.short_description = "Unflag selected comments"


# ----------------------------------------------------
# 3. Customizing ContentAttachment Admin
# ----------------------------------------------------
@admin.register(ContentAttachment)
class ContentAttachmentAdmin(admin.ModelAdmin):
    """
    Customizes the display and interaction for the ContentAttachment model in the admin.
    """
    list_display = ('description', 'file_name', 'related_object', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('description', 'file', 'image')

    # Custom method to display the file name nicely
    def file_name(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]
        elif obj.image:
            return obj.image.name.split('/')[-1]
        return 'N/A'
    file_name.short_description = 'File Name'

    # Custom method to show which object (discussion or comment) it's related to
    def related_object(self, obj):
        if obj.discussion:
            return f'Discussion: {obj.discussion.title}'
        elif obj.comment:
            return f'Comment: {obj.comment.id}'
        return 'None'
    related_object.short_description = 'Related To'

    # Ensure only one of discussion or comment is set, or neither.
    # You might want to use custom form validation for this in a real app.
    # For display, we ensure clarity.