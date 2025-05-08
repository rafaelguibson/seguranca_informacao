from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
import uuid

from .forms import CadastroForm, LoginForm, AtualizarForm, EsqueciSenhaForm
from .models import (
    Users, UserSalt, UserPassword, UserLog, VerificationToken
)

# Armazena tokens temporários
reset_tokens = {}

def cadastrar(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            salt_obj = UserSalt.objects.create(user=user)
            senha_obj = UserPassword(user=user)
            senha_obj.set_password(form.cleaned_data['senha'], salt_obj.salt)
            senha_obj.save()

            token = VerificationToken.objects.create(user=user)
            link = request.build_absolute_uri(reverse('verificar_email', args=[token.token]))

            send_mail(
                subject='Verifique seu cadastro',
                message=f'Olá {user.nome}, clique no link para confirmar seu cadastro:\n\n{link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            messages.success(request, "Cadastro criado! Verifique seu e-mail.")
            return redirect('login')
    else:
        form = CadastroForm()
    return render(request, 'accounts/register.html', {'form': form})

def verificar_email(request, token):
    try:
        token_obj = VerificationToken.objects.get(token=token, used=False)
        user = token_obj.user
        user.is_active = True
        user.save()

        token_obj.used = True
        token_obj.save()

        messages.success(request, "Conta verificada com sucesso!")
        return redirect('login')

    except VerificationToken.DoesNotExist:
        messages.error(request, "Token inválido ou expirado.")
        return redirect('login')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = Users.objects.get(email=form.cleaned_data['email'])
                if not user.is_active:
                    messages.warning(request, "Conta ainda não verificada. Verifique seu e-mail.")
                else:
                    salt = UserSalt.objects.get(user=user)
                    senha = UserPassword.objects.get(user=user)
                    if senha.check_password(form.cleaned_data['senha'], salt.salt):
                        request.session['user_id'] = str(user.id)
                        user.ultimo_acesso = timezone.now()
                        user.save()
                        UserLog.objects.create(user=user, acao="Login realizado")
                        messages.success(request, "Login realizado com sucesso!")
                        return redirect('dashboard')
                    else:
                        messages.error(request, "Senha incorreta.")
            except Users.DoesNotExist:
                messages.error(request, "Usuário não encontrado.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = Users.objects.get(id=user_id)
    return render(request, 'accounts/dashboard.html', {'user': user})

def profile_update(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = Users.objects.get(id=user_id)
    if request.method == 'POST':
        form = AtualizarForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            UserLog.objects.create(user=user, acao="Perfil atualizado")
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('dashboard')
    else:
        form = AtualizarForm(instance=user)
    return render(request, 'accounts/profile_update.html', {'form': form})

def password_change(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = Users.objects.get(id=user_id)
    salt = UserSalt.objects.get(user=user)
    senha = UserPassword.objects.get(user=user)

    if request.method == 'POST':
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        nova_senha_confirm = request.POST.get('nova_senha_confirm')

        if not senha.check_password(senha_atual, salt.salt):
            messages.error(request, "Senha atual incorreta.")
        elif nova_senha != nova_senha_confirm:
            messages.error(request, "As novas senhas não coincidem.")
        else:
            senha.set_password(nova_senha, salt.salt)
            senha.save()
            UserLog.objects.create(user=user, acao="Senha alterada")
            messages.success(request, "Senha alterada com sucesso!")
            return redirect('dashboard')

    return render(request, 'accounts/password_change.html')

def password_reset_request(request):
    if request.method == 'POST':
        form = EsqueciSenhaForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = Users.objects.get(email=email)
                token = str(uuid.uuid4())
                reset_tokens[token] = str(user.id)

                reset_link = request.build_absolute_uri(
                    reverse('password_reset_confirm', args=[token])
                )
                send_mail(
                    subject='Recuperação de Senha',
                    message=f'Clique no link para redefinir sua senha: {reset_link}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )
                UserLog.objects.create(user=user, acao="Solicitação de redefinição de senha")
                messages.success(request, "Email de redefinição de senha enviado.")
                return redirect('password_reset_done')
            except Users.DoesNotExist:
                messages.success(request, "Se o email existir, você receberá instruções.")
                return redirect('password_reset_done')
    else:
        form = EsqueciSenhaForm()
    return render(request, 'accounts/password_reset_form.html', {'form': form})

def password_reset_done(request):
    return render(request, 'accounts/password_reset_done.html')

def password_reset_confirm(request, token):
    user_id = reset_tokens.get(token)
    if not user_id:
        return render(request, 'accounts/password_reset_confirm.html', {'validlink': False})

    user = Users.objects.get(id=user_id)
    salt = UserSalt.objects.get(user=user)
    senha = UserPassword.objects.get(user=user)

    if request.method == 'POST':
        nova = request.POST.get('nova_senha')
        confirmar = request.POST.get('confirmar_senha')
        if nova == confirmar:
            senha.set_password(nova, salt.salt)
            senha.save()
            UserLog.objects.create(user=user, acao="Senha redefinida via reset")
            del reset_tokens[token]
            messages.success(request, "Senha redefinida com sucesso.")
            return redirect('password_reset_complete')
        else:
            messages.error(request, "As senhas não coincidem.")

    return render(request, 'accounts/password_reset_confirm.html', {'validlink': True})

def password_reset_complete(request):
    return render(request, 'accounts/password_reset_complete.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')
