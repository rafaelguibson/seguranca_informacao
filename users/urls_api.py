# users/urls.py
from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    ChangePasswordView,
    UserLogoutView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
]

