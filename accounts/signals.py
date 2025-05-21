from django.db.models.signals import post_save
from django.dispatch import receiver # Decorator to register a signal receiver
from .models import CustomUser, UserProfile

@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Creates a UserProfile when a new CustomUser is created.
    Updates an existing UserProfile when a CustomUser is saved.
    """
    if created:
        UserProfile.objects.create(user=instance)
    # Optional: If you need to update the profile when the user is saved (e.g., if user has a direct link to profile)
    # else:
    #    instance.userprofile.save() # Ensure the profile object is also saved if necessary