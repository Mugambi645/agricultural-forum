from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views # Import built-in views for password reset/login
from . import views

app_name = "accounts"


urlpatterns = [
    # Custom Registration and Activation
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('activate/<str:uidb64>/<str:token>/', views.activate_account, name='activate_account'),
    path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),

    # Built-in Login and Logout (using Django's views for simplicity, though you can override them)
    path('login/', views.CustomLoginView.as_view(), name='login'), 
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),

    # Profile Management
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_update_view, name='profile_update'),

    # Password Change (using custom view that inherits from built-in)
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),

    # Password Reset (Django's built-in views)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html', email_template_name='registration/password_reset_email.html', success_url=reverse_lazy('password_reset_done')), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html', success_url=reverse_lazy('password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Account Deletion
    path('account_delete_confirm/', views.account_delete_confirm, name='account_delete_confirm'),

    # Example home page (if users app serves home)
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='home'), # Redirect non-logged in users to login
]