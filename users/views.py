from django.shortcuts import render
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
    return render(request, 'core/cadastro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = Users.objects.get(email=form.cleaned_data['email'])
                if user.check_password(form.cleaned_data['senha']):
                    user.ultimo_acesso = timezone.now()
                    user.save()
                    UserLog.objects.create(user=user, acao="Login realizado")
                    request.session['user_id'] = str(user.id)
                    return redirect('painel')
                else:
                    messages.error(request, "Senha incorreta.")
            except Users.DoesNotExist:
                messages.error(request, "Usuário não encontrado.")
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})

def painel(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = Users.objects.get(id=user_id)
    if request.method == 'POST':
        form = AtualizarForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            UserLog.objects.create(user=user, acao="Dados atualizados")
            messages.success(request, "Dados atualizados com sucesso!")
            return redirect('painel')
    else:
        form = AtualizarForm(instance=user)
    return render(request, 'core/painel.html', {'form': form})

def esqueci_senha(request):
    if request.method == 'POST':
        form = EsqueciSenhaForm(request.POST)
        if form.is_valid():
            try:
                user = Users.objects.get(email=form.cleaned_data['email'])
                UserLog.objects.create(user=user, acao="Solicitação de recuperação de senha")
                messages.success(request, "Se o email existir, enviamos instruções.")
            except Users.DoesNotExist:
                pass
            return redirect('login')
    else:
        form = EsqueciSenhaForm()
    return render(request, 'core/esqueci_senha.html', {'form': form})

