
from django.contrib import admin
from .models import Discussion, Comment, ContentAttachment
# REMOVE THIS LINE: from location_field.admin import plain as admin_plain
# You DO NOT need to import anything specific from location_field.admin
# The PlainLocationField model field itself will render the map widget in the admin.

# ----------------------------------------------------
# 1. Customizing Discussion Admin
# ----------------------------------------------------
class ContentAttachmentInline(admin.TabularInline):
    """
    Allows managing attachments directly from the Discussion/Comment admin page.
    """
    model = ContentAttachment
    extra = 1 # Number of empty forms to display
    fields = ('file', 'image', 'description') # Fields to display in the inline form

@admin.register(Discussion) # This decorator is equivalent to admin.site.register(Discussion, DiscussionAdmin)
class DiscussionAdmin(admin.ModelAdmin):
    """
    Customizes the display and interaction for the Discussion model in the admin.
    """
    list_display = ('title', 'author', 'created_at', 'updated_at', 'location_display') # Add location to list display
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
            'fields': ('title', 'content', 'location') # Include location here. This is where the magic happens for the map widget.
        }),
        ('Metadata', {
            'fields': ('author',),
            'classes': ('collapse',), # Makes this section collapsible
        }),
    )

    # Custom method to display location coordinates in a readable format
    def location_display(self, obj):
        if obj.location:
            # Assuming location is stored as "latitude,longitude"
            parts = obj.location.split(',')
            if len(parts) == 2:
                try:
                    lat = float(parts[0])
                    lon = float(parts[1])
                    return f"Lat: {lat:.4f}, Lon: {lon:.4f}" # Format to 4 decimal places
                except ValueError:
                    return obj.location # Return raw if parsing fails
        return "N/A"
    location_display.short_description = 'Location'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'discussion', 'author', 'created_at', 'votes', 'is_flagged', 'parent') # Include votes and parent
    list_filter = ('created_at', 'author', 'is_flagged', 'is_deleted')  # Add is_deleted
    search_fields = ('content', 'author__username', 'discussion__title')
    raw_id_fields = ('discussion', 'author', 'parent') # Add parent
    date_hierarchy = 'created_at'
    ordering = ('-votes', '-created_at')  # Order by votes, then date

    fieldsets = (
        (None, {
            'fields': ('discussion', 'author', 'content', 'parent') # Include parent
        }),
        ('Moderation Status', {
            'fields': ('is_flagged', 'flag_reason', 'is_deleted'),  # Add is_deleted
            'classes': ('collapse',),
            'description': 'AI-moderated flagging status. Flagged comments might require review.'
        }),
        ('Voting', {
            'fields': ('votes',),  # Add votes
            'classes': ('collapse',),
        }),
    )

    actions = ['unflag_comments', 'soft_delete_comments']

    def unflag_comments(self, request, queryset):
        updated_count = queryset.update(is_flagged=False, flag_reason=None)
        self.message_user(request, f'{updated_count} comments successfully unflagged.', level=admin.messages.SUCCESS)
    unflag_comments.short_description = "Unflag selected comments"

    def soft_delete_comments(self, request, queryset):
        updated_count = queryset.update(is_deleted=True)
        self.message_user(request, f'{updated_count} comments soft-deleted.', level=admin.messages.SUCCESS)
    soft_delete_comments.short_description = "Soft-delete selected comments"

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
    raw_id_fields = ('discussion', 'comment') # Use raw ID for ForeignKey

    def file_name(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]
        elif obj.image:
            return obj.image.name.split('/')[-1]
        return 'N/A'
    file_name.short_description = 'File Name'

    def related_object(self, obj):
        if obj.discussion:
            return f'Discussion: {obj.discussion.title}'
        elif obj.comment:
            return f'Comment: {obj.comment.id}'
        return 'None'
    related_object.short_description = 'Related To'