from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator # For email verification
from django.db import transaction

from .forms import CustomUserCreationForm, UserProfileUpdateForm, CustomPasswordChangeForm
from .models import CustomUser, UserProfile 
# --- Registration View ---
class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login') # Redirect to login after successful registration

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False # User is inactive until email is verified
        user.save()

        # Send verification email
        current_site = get_current_site(self.request)
        mail_subject = 'Activate your AgriForum account.'
        message = render_to_string('registration/account_activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': default_token_generator.make_token(user), # Use default_token_generator
            'token': default_token_generator.make_token(user),
        })
        to_email = form.cleaned_data.get('email')
        try:
            send_mail(mail_subject, strip_tags(message), 'no-reply@yourdomain.com', [to_email], html_message=message)
            messages.info(self.request, 'Please confirm your email address to complete the registration. A verification link has been sent to your email.')
        except Exception as e:
            messages.error(self.request, f'Failed to send verification email: {e}. Please contact support.')
            user.delete() # Clean up created user if email fails
            return self.form_invalid(form)

        return redirect('account_activation_sent') # Custom URL for showing a message

# --- Email Verification View ---
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.email_verified = True
        user.save()
        auth_login(request, user) # Log in the user after verification
        messages.success(request, 'Thank you for your email confirmation. Your account has been activated and you are now logged in!')
        return redirect(reverse_lazy('home:index')) # Redirect to home or profile page
    else:
        messages.error(request, 'Activation link is invalid or has expired!')
        return render(request, 'registration/account_activation_invalid.html')

def account_activation_sent(request):
    return render(request, 'registration/account_activation_sent.html')

# --- User Profile View ---
@login_required
def profile_view(request):
    # Retrieve the user's profile, it should exist due to the signal
    profile = request.user.userprofile
    context = {
        'profile': profile,
        'user': request.user # Pass user object too if needed
    }
    return render(request, 'users/profile.html', context)

# --- User Profile Update View ---
@login_required
def profile_update_view(request):
    profile = request.user.userprofile # Get the existing profile
    if request.method == 'POST':
        # Pass instance=profile to update the existing profile
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'There was an error updating your profile. Please correct the errors below.')
    else:
        form = UserProfileUpdateForm(instance=profile) # Pre-fill form with existing profile data
    return render(request, 'users/profile_update.html', {'form': form})

# --- Custom Password Change View ---
class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('password_change_done') # Django's built-in success URL for password change

    def form_valid(self, form):
        messages.success(self.request, 'Your password was changed successfully!')
        return super().form_valid(form)

# --- Account Deletion View ---
@login_required
def account_delete_confirm(request):
    if request.method == 'POST':
        user = request.user
        username = user.username # Store username for confirmation message
        try:
            with transaction.atomic():
                user.delete()
                # Django's logout_then_login might not work well after account deletion
                # So we manually log out and redirect
                from django.contrib.auth import logout
                logout(request)
            messages.success(request, f"Your account '{username}' has been successfully deleted.")
            return redirect(reverse_lazy('login')) # Redirect to login page
        except Exception as e:
            messages.error(request, f"There was an error deleting your account: {e}")
            return redirect('accounts:profile') # Redirect back to profile if deletion fails
    return render(request, 'users/account_delete_confirm.html')