from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
from .forms import LoginForm, CadastroForm


@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def login_view(request):
    if request.user.is_authenticated:
        return redirect('contratos:dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'contratos:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def cadastro_view(request):
    if request.user.is_authenticated:
        return redirect('contratos:dashboard')

    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f'Bem-vindo(a), {user.first_name}! Sua conta foi criada.'
            )
            return redirect('contratos:dashboard')
    else:
        form = CadastroForm()

    return render(request, 'accounts/cadastro.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')