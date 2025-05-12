# users/views.py
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer, UserProfileSerializer, ChangePasswordSerializer

class UserRegistrationView(generics.CreateAPIView):
    """
    View para registrar novos usuários.
    Permite que qualquer usuário (AllowAny) crie uma nova conta.
    Utiliza o UserSerializer para validar e criar o usuário.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Cria um token para o novo usuário após o registro bem-sucedido
        token, created = Token.objects.get_or_create(user=user)
        headers = self.get_success_headers(serializer.data)
        # Retorna os dados do usuário e o token
        return Response(
            {
                "user": serializer.data,
                "token": token.key
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class UserLoginView(APIView):
    """
    View para login de usuários.
    Permite que qualquer usuário (AllowAny) tente fazer login.
    Retorna um token de autenticação se as credenciais forem válidas.
    """
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "user_id": user.pk, "email": user.email, "username": user.username}, status=status.HTTP_200_OK)
        return Response({"error": "Credenciais inválidas"}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View para visualizar e atualizar o perfil do usuário autenticado.
    Requer que o usuário esteja autenticado (IsAuthenticated).
    Utiliza o UserProfileSerializer para exibir e atualizar os dados.
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        # Retorna o objeto do usuário que está fazendo a requisição.
        return self.request.user

class ChangePasswordView(APIView):
    """
    View para permitir que um usuário autenticado altere sua senha.
    Requer que o usuário esteja autenticado (IsAuthenticated).
    Utiliza o ChangePasswordSerializer para validar a senha antiga e definir a nova.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            # Verifica a senha antiga
            if not user.check_password(serializer.validated_data.get("old_password")):
                return Response({"old_password": ["Senha antiga incorreta."]}, status=status.HTTP_400_BAD_REQUEST)
            # Define a nova senha
            user.set_password(serializer.validated_data.get("new_password"))
            user.save()
            return Response({"status": "Senha alterada com sucesso"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    """
    View para logout de usuários (invalidando o token).
    Requer que o usuário esteja autenticado.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            # Simplesmente deleta o token do usuário para efetuar o logout
            request.user.auth_token.delete()
            return Response({"status": "Logout realizado com sucesso"}, status=status.HTTP_200_OK)
        except (AttributeError, Token.DoesNotExist):
            return Response({"error": "Nenhum token encontrado para este usuário ou token já invalidado."}, status=status.HTTP_400_BAD_REQUEST)

