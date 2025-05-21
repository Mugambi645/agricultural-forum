from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from accounts.models import CustomUser, UserProfile # Import CustomUser and UserProfile (if using signals)

class LoginTests(TestCase):

    def setUp(self):
        # Initialize the test client
        self.client = Client()

        # Create an active, verified test user
        self.active_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
        }
        self.active_user = CustomUser.objects.create_user(
            username=self.active_user_data['username'],
            email=self.active_user_data['email'],
            password=self.active_user_data['password'],
            is_active=True,         # This user is active
            email_verified=True     # This user's email is verified
        )
        # Ensure a UserProfile exists for the active user (important for signals approach)
        # The post_save signal should create this, but explicit check or creation for tests is safe.
        if not hasattr(self.active_user, 'userprofile'):
            UserProfile.objects.create(user=self.active_user)


        # Create an inactive, unverified test user (simulates user who hasn't clicked verification link)
        self.inactive_user_data = {
            'username': 'inactiveuser',
            'email': 'inactive@example.com',
            'password': 'password123',
        }
        self.inactive_user = CustomUser.objects.create_user(
            username=self.inactive_user_data['username'],
            email=self.inactive_user_data['email'],
            password=self.inactive_user_data['password'],
            is_active=False,        # This user is inactive
            email_verified=False    # This user's email is not verified
        )
        # Ensure a UserProfile exists for the inactive user
        if not hasattr(self.inactive_user, 'userprofile'):
            UserProfile.objects.create(user=self.inactive_user)


    def test_login_page_loads_correctly(self):
        """
        Test that the login page returns a 200 OK status code and uses the correct template.
        """
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertContains(response, 'Log In to AgriForum') # Check for some text on the page

    def test_successful_login(self):
        """
        Test that a user can successfully log in with correct credentials.
        """
        response = self.client.post(reverse('accounts:login'), {
            'username': self.active_user_data['username'],
            'password': self.active_user_data['password']
        }, follow=True) # follow=True to follow redirects

        self.assertEqual(response.status_code, 200) # Should be 200 after following the redirect
        self.assertRedirects(response, reverse('home:index')) # Should redirect to LOGIN_REDIRECT_URL
        self.assertTrue(response.context['user'].is_authenticated) # User should be authenticated
        self.assertEqual(response.context['user'].username, self.active_user.username)

        messages = list(get_messages(response.wsgi_request))
        self.assertFalse(any(m.tags == 'error' for m in messages)) # No error messages on successful login

    def test_login_with_incorrect_password(self):
        """
        Test that login fails with an incorrect password and displays an error message.
        """
        response = self.client.post(reverse('accounts:login'), {
            'username': self.active_user_data['username'],
            'password': 'wrongpassword' # Incorrect password
        }, follow=True)

        self.assertEqual(response.status_code, 200) # Stays on login page (or redirects back to it)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertFalse(response.context['user'].is_authenticated) # User should NOT be logged in

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(m.tags == 'error' for m in messages)) # Expect an error message
        # Check for the specific error message added in CustomLoginView's form_invalid
        self.assertIn('Please enter a correct username and password.', str(messages[0]))


    def test_login_with_non_existent_username(self):
        """
        Test that login fails with a non-existent username and displays an error message.
        """
        response = self.client.post(reverse('accounts:login'), {
            'username': 'nonexistentuser', # Non-existent username
            'password': 'password123'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertFalse(response.context['user'].is_authenticated)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(m.tags == 'error' for m in messages))
        # Check for the specific error message added in CustomLoginView's form_invalid
        self.assertIn('Please enter a correct username and password.', str(messages[0]))


    def test_login_with_inactive_user(self):
        """
        Test that an inactive user cannot log in and displays an error message.
        This covers users who have not yet verified their email if is_active is set to False
        until email verification.
        """
        response = self.client.post(reverse('login'), {
            'username': self.inactive_user_data['username'],
            'password': self.inactive_user_data['password']
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertFalse(response.context['user'].is_authenticated) # User should NOT be logged in

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(m.tags == 'error' for m in messages))
        # The specific message for inactive users is usually "This account is inactive."
        # If your CustomLoginView also uses the generic message for inactive accounts,
        # adjust this assertion accordingly.
        self.assertIn('Please enter a correct username and password', str(messages[0]))
        # If you implemented a specific message for inactive users, it might be:
        # self.assertIn('This account is inactive.', str(messages[0]))


    def test_logout(self):
        """
        Test that a logged-in user can successfully log out via a POST request.
        """
        # 1. Log in the user to establish a session
        login_response = self.client.post(reverse('accounts:login'), {
            'username': self.active_user_data['username'],
            'password': self.active_user_data['password']
        }, follow=True)
        # Ensure user is logged in before testing logout
        self.assertTrue(login_response.context['user'].is_authenticated)

        # 2. Attempt to log out using a POST request (LogoutView usually expects POST)
        response = self.client.post(reverse('accounts:logout'), follow=True) # Changed from get to post

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('accounts:login')) # Should redirect to LOGOUT_REDIRECT_URL
        self.assertFalse(response.context['user'].is_authenticated) # User should be logged out
     