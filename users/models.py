from django.db import models
import uuid
import pyautogui
import hashlib
import os
from django.utils import timezone

def get_pointer_location():
    try:
        x, y = pyautogui.position()
        return x * y
    except:
        return 1  # fallback caso falhe

def generate_salt():
    return os.urandom(16).hex() + str(get_pointer_location())

def hash_with_salt(data, salt):
    return hashlib.sha256((salt + data).encode('utf-8')).hexdigest()

class Users(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    data_nascimento = models.DateField()
    is_active = models.BooleanField(default=False)  # Só ativa após confirmação por email
    created_at = models.DateTimeField(auto_now_add=True)
    ultimo_acesso = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email

class UserSalt(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    salt = models.CharField(max_length=100, default=generate_salt)

    def __str__(self):
        return f"Salt de {self.user.email}"

class UserPassword(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    password_hash = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password, salt):
        self.password_hash = hash_with_salt(raw_password, salt)

    def check_password(self, raw_password, salt):
        return self.password_hash == hash_with_salt(raw_password, salt)

    def __str__(self):
        return f"Senha hash de {self.user.email}"

class VerificationToken(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Token de {self.user.email}"

class UserLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    acao = models.CharField(max_length=255)
    data_hora = models.DateTimeField(auto_now_add=True)
    salt = models.CharField(max_length=100, default=generate_salt)
    hash_acao = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        self.hash_acao = hash_with_salt(self.acao, self.salt)
        super().save(*args, **kwargs)
