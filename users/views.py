from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from .forms import CadastroForm, LoginForm, AtualizarForm, EsqueciSenhaForm
from .models import Users, UserLog
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
import uuid

# Armazena tokens de reset temporariamente (em produção use cache seguro)
reset_tokens = {}

def cadastrar(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['senha'])
            user.save()
            UserLog.objects.create(user=user, acao="Cadastro realizado")
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect('login')
    else:
        form = CadastroForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = Users.objects.get(email=form.cleaned_data['email'])
                if user.check_password(form.cleaned_data['senha']):
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

    if request.method == 'POST':
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        nova_senha_confirm = request.POST.get('nova_senha_confirm')

        if not user.check_password(senha_atual):
            messages.error(request, "Senha atual incorreta.")
        elif nova_senha != nova_senha_confirm:
            messages.error(request, "As novas senhas não coincidem.")
        else:
            user.set_password(nova_senha)
            user.save()
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

    if request.method == 'POST':
        senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        if senha == confirmar_senha:
            user.set_password(senha)
            user.save()
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
