from django.urls import path
from .views import RegistrationView, LoginView

"""
URL patterns for user authentication.

Endpoints:

- POST /registration/  
  Registers a new user.  
  Accepts: full name, email, password, repeated password.  
  Returns: user data on success or validation errors.

- POST /login/  
  Logs in a user.  
  Accepts: email and password.  
  Returns: user data on success or authentication error.
"""
urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login')
]