from django.contrib import auth, messages
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect

from accounts.form import RegisterForm, LoginForm, SecondRegisterForm
from accounts.models import Profile


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return redirect('accounts:second_register')

    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })


def second_register(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={'username': request.user.username},
    )

    if request.method == "POST":
        form = SecondRegisterForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('build:home')
    else:
        form = SecondRegisterForm(instance=profile)
    return render(request, 'accounts/second_register.html', {'form': form})


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

    return render(request, 'accounts/login.html', {
        'form': form
    })

def logout(request):
    auth_logout(request)
    return redirect('accounts:login')
