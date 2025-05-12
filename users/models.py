from django.db import models
import uuid
import hashlib
import os

def generate_salt():
    return os.urandom(16).hex()

# Adicionar captura da posição do mouse para o sal
def hash_with_salt(data, salt):
    return hashlib.sha256((salt + data).encode('utf-8')).hexdigest()

class Users(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    data_nascimento = models.DateField()
    senha = models.CharField(max_length=255)
    salt = models.CharField(max_length=32, default=generate_salt)
    ultimo_acesso = models.DateTimeField(null=True, blank=True)

    def set_password(self, raw_password):
        self.salt = generate_salt()
        self.senha = hash_with_salt(raw_password, self.salt)
    
    def check_password(self, raw_password):
        return self.senha == hash_with_salt(raw_password, self.salt)

    def __str__(self):
        return self.nome

class UserLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    acao = models.CharField(max_length=255)
    data_hora = models.DateTimeField(auto_now_add=True)
    salt = models.CharField(max_length=32, default=generate_salt)
    hash_acao = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        self.hash_acao = hash_with_salt(self.acao, self.salt)
        super().save(*args, **kwargs)

