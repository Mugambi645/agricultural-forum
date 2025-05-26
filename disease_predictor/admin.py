
from django.contrib import admin
from .models import DiseasePrediction

@admin.register(DiseasePrediction)
class DiseasePredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'image_thumbnail', 'prediction_label', 'confidence', 'predicted_at')
    list_filter = ('prediction_label', 'predicted_at', 'user')
    search_fields = ('prediction_label', 'user__username')
    readonly_fields = ('image_preview',) # To display image in admin detail view

    def image_thumbnail(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: contain;" />'
        return "No Image"
    image_thumbnail.short_description = 'Thumbnail'
    image_thumbnail.allow_tags = True

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="200" height="200" style="object-fit: contain;" />'
        return "No Image"
    image_preview.short_description = 'Image Preview'
    image_preview.allow_tags = True