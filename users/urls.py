from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.cadastrar, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('password/change/', views.password_change, name='password_change'),
    path('logout/', views.logout_view, name='logout'),
]

