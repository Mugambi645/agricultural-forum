
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, UserProfile

admin.site.register(UserProfile)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username', 'email_verified', 'is_staff', 'is_active']
    # 'email_verified' is directly on CustomUser, so it's correctly placed here.
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('email_verified',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email',)}), # This adds 'email' to the new user creation form in admin
    )