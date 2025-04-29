from django import forms
from .models import Users
import re

class CadastroForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Users
        fields = ['nome', 'email', 'data_nascimento', 'senha']

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

class LoginForm(forms.Form):
    email = forms.EmailField()
    senha = forms.CharField(widget=forms.PasswordInput)

class AtualizarForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['nome', 'email', 'data_nascimento']

class EsqueciSenhaForm(forms.Form):
    email = forms.EmailField()
