# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import CustomUser, UserProfile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field

# For user registration: only fields on CustomUser
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email',) # username and email are inherited from AbstractUser

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username'),
            Field('email'),
            Field('password'),
            Field('password2'),
            Submit('submit', 'Register', css_class='btn btn-success mt-3')
        )

# For Django Admin User editing: fields on CustomUser
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        # These fields are inherited from AbstractUser, PLUS 'email_verified'
        # which is *explicitly* defined on your CustomUser model.
        fields = (
            'username', 'email', 'is_active', 'is_staff', 'is_superuser',
            'groups', 'user_permissions', 'email_verified' # THIS MUST MATCH your CustomUser model
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username'),
            Field('email'),
            Field('email_verified'), # This too must match
            Field('is_active'),
            Field('is_staff'),
            Field('is_superuser'),
            Field('groups'),
            Field('user_permissions'),
            Submit('submit', 'Update User', css_class='btn btn-primary mt-3')
        )

# For user's public profile editing: fields on UserProfile
class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'location', 'bio', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('phone_number'),
            Field('location'),
            Field('bio'),
            Field('profile_picture'),
            Submit('submit', 'Update Profile', css_class='btn btn-primary mt-3')
        )

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('old_password'),
            Field('new_password1'),
            Field('new_password2'),
            Submit('submit', 'Change Password', css_class='btn btn-warning mt-3')
        )