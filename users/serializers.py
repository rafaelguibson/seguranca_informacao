# users/serializers.py
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    # Definimos o campo de senha como write_only para que não seja retornado nas respostas da API
    # e aplicamos as validações de senha do Django.
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        # Campos a serem serializados/desserializados.
        # Incluímos username, password, password_confirm e email para o registro.
        fields = ('id', 'username', 'password', 'password_confirm', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate(self, attrs):
        # Validamos se as senhas fornecidas (password e password_confirm) são iguais.
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."}) 
        return attrs

    def create(self, validated_data):
        # Removemos o campo password_confirm, pois ele não faz parte do modelo User.
        validated_data.pop('password_confirm')
        # Criamos o usuário utilizando o método create_user para garantir que a senha seja hasheada corretamente.
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Campos a serem expostos para visualização e atualização do perfil.
        # A senha não é incluída aqui por motivos de segurança.
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('username', 'id') # Username e ID não devem ser alterados diretamente por esta view

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "As novas senhas não coincidem."}) 
        return attrs

