from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastrar, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('painel/', views.painel, name='painel'),
    path('esqueci-senha/', views.esqueci_senha, name='esqueci_senha'),
]
