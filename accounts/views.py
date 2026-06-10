from django.contrib import auth, messages
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect
from accounts.form import RegisterForm, LoginForm, SecondRegisterForm
from accounts.models import Profile
from build.models import BuilderProfile # 👈 Xatolik chiqmasligi uchun shu yerga import qo'shildi

# 1. BIRINCHI BOSQICH: Standart ro'yxatdan o'tish
def register(request):
    if request.user.is_authenticated:
        return redirect('build:home')

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return redirect('accounts:second_register')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


# 2. IKKINCHI BOSQICH: Rol tanlash va Profil ma'lumotlarini to'ldirish
def second_register(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = SecondRegisterForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            updated_profile = form.save()

            # 🔥 ROLLAR LOGIKASI:
            if updated_profile.role == 'builder':
                BuilderProfile.objects.get_or_create(
                    profile=updated_profile,
                    defaults={'profession': 'Usta', 'experience_years': 0}
                )
                messages.success(request, "Profil muvaffaqiyatli yaratildi! Endi ustalik ma'lumotlaringizni to'ldirishingiz mumkin.")
            else:
                messages.success(request, "Xush kelibsiz! Profilingiz muvaffaqiyatli faollashtirildi.")

            return redirect('build:home')
    else:
        form = SecondRegisterForm(instance=profile)

    return render(request, 'accounts/second_register.html', {'form': form})


# 3. TIZIMGA KIRISH (Login)
def login(request):
    if request.user.is_authenticated:
        return redirect('build:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect('build:home')
            else:
                messages.error(request, 'Foydalanuvchi nomi yoki parol noto\'g\'ri!')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


# 4. TIZIMDAN CHIQISH (Logout)
def logout(request):
    auth_logout(request)
    return redirect('accounts:login')