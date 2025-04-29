from django.shortcuts import render, redirect
from .forms import CadastroForm, LoginForm, AtualizarForm, EsqueciSenhaForm
from .models import Users, UserLog
from django.utils import timezone
from django.contrib import messages

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
    return render(request, 'register.html', {'form': form})

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
    return render(request, 'login.html', {'form': form})

def dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = Users.objects.get(id=user_id)
    return render(request, 'dashboard.html', {'user': user})

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
    return render(request, 'profile_update.html', {'form': form})

def password_change(request):
    # Simples tela de mudança de senha
    if request.method == 'POST':
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        nova_senha_confirm = request.POST.get('nova_senha_confirm')

        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
        user = Users.objects.get(id=user_id)

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

    return render(request, 'password_change.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')
