from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Adiciona um novo caminho para a API, prefixado com 'api/users/', que incluirá as URLs da API do app 'users'.
    path('api/users/', include('users.urls_api')), 
]

