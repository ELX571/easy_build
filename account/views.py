from django.contrib import auth, messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from account.form import RegisterForm, LoginForm, SecondRegisterForm
from account.models import Role, Profile


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            request.session['role'] = form.cleaned_data['role']
            request.session['first_name'] = form.cleaned_data['first_name']
            request.session['last_name'] = form.cleaned_data['last_name']

            return redirect('second_register')

    else:
        form = RegisterForm()

    return render(request, 'account/register.html', {
        'form': form
    })


def second_register(request):
    if request.method == "POST":
        form = SecondRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            return redirect('build:home')
    else:
        form = SecondRegisterForm()
    return render(request, 'account/second_register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(
                username=username,
                password=password
            )

            if user is not None:
                auth.login(request, user)
                return redirect('build:home')
            else:
                messages.error(request, 'Username or password is incorrect')

    else:
        form = LoginForm()

    return render(request, 'account/login.html', {
        'form': form
    })

def logout(request):
    auth_logout(request)
    return redirect('account:login')


