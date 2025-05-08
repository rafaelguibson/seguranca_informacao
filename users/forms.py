from django import forms
from .models import Users
import re

class CadastroForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput, label="Senha")
    confirmar_senha = forms.CharField(widget=forms.PasswordInput, label="Confirmar Senha")

    class Meta:
        model = Users
        fields = ['nome', 'email', 'data_nascimento', 'senha']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Users.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean_senha(self):
        senha = self.cleaned_data.get('senha')
        if len(senha) < 8:
            raise forms.ValidationError("A senha deve ter no mínimo 8 caracteres.")
        if not re.search(r'[A-Z]', senha):
            raise forms.ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
        if not re.search(r'[a-z]', senha):
            raise forms.ValidationError("A senha deve conter pelo menos uma letra minúscula.")
        if not re.search(r'[0-9]', senha):
            raise forms.ValidationError("A senha deve conter pelo menos um número.")
        if not re.search(r'[\W_]', senha):
            raise forms.ValidationError("A senha deve conter pelo menos um caractere especial.")
        return senha

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get('senha')
        confirmar = cleaned_data.get('confirmar_senha')

        if senha and confirmar and senha != confirmar:
            self.add_error('confirmar_senha', "As senhas não coincidem.")

class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    senha = forms.CharField(widget=forms.PasswordInput, label="Senha")

class AtualizarForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['nome', 'email', 'data_nascimento']

class EsqueciSenhaForm(forms.Form):
    email = forms.EmailField(label="Email")
