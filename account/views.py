from django.contrib import auth, messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

from account.form import RegisterForm, LoginForm
from account.models import Role


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            Role.objects.create(
                user=user,
                role=form.cleaned_data['role'],
            )

            return redirect('build:home_page')

    else:
        form = RegisterForm()

    return render(request, 'account/register.html', {
        'form': form
    })


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
                return redirect('build:home_page')
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


