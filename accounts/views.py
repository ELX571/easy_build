from django.contrib.auth import (
    logout as auth_logout,
    login as auth_login,
    authenticate,
)
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from accounts.models import Profile
from accounts.form import RegisterForm, LoginForm, ProfileEditForm
from accounts.serializers import (
    UserLoginSerializer,
    UserRegisterSerializer,
    UserSecondRegisterSerializer,
    ProfileSerializer,
)
from build.models import BuilderProfile


# =============================================================================
# AUTH VIEWSET — API (DRF)
# =============================================================================

class AuthViewSet(viewsets.GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = UserLoginSerializer

    def get_permissions(self):
        if self.action in ['profile_me', 'logout_user']:
            return [IsAuthenticated()]
        return [AllowAny()]

    # ── LOGIN ─────────────────────────────────────────────────────────────────
    @action(methods=['post'], detail=False, url_path='login', url_name='login-api')
    def login_api(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        auth_login(request, user)
        return Response({'detail': 'Muvaffaqiyatli kirdingiz!'}, status=status.HTTP_200_OK)

    # ── REGISTER ──────────────────────────────────────────────────────────────
    @action(methods=['post'], detail=False, url_path='register', url_name='register-api')
    def register_api(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, user)
        return Response(
            {'detail': "Ro'yxatdan o'tdingiz!"},
            status=status.HTTP_201_CREATED
        )

    # ── SECOND REGISTER (Profil to'ldirish) ───────────────────────────────────
    @action(methods=['post'], detail=False, url_path='second-register', url_name='second-register-api')
    def second_register_api(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': "Avval tizimga kiring."}, status=status.HTTP_401_UNAUTHORIZED)

        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = UserSecondRegisterSerializer(
            instance=profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()

        if updated.role in ['builder', 'team']:
            profession = 'Kompaniya/Jamoa' if updated.role == 'team' else 'Usta'
            BuilderProfile.objects.get_or_create(
                profile=updated,
                defaults={'profession': profession, 'experience_years': 0}
            )

        return Response({'detail': "Profil muvaffaqiyatli to'ldirildi!"}, status=status.HTTP_200_OK)

    # ── LOGOUT ────────────────────────────────────────────────────────────────
    @action(methods=['post'], detail=False, url_path='logout', url_name='logout-api')
    def logout_api(self, request):
        auth_logout(request)
        return Response({'detail': 'Tizimdan chiqdingiz.'}, status=status.HTTP_200_OK)

    # ── PROFILE ME ────────────────────────────────────────────────────────────
    @action(methods=['get'], detail=False, url_path='me', url_name='me')
    def profile_me(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)


# =============================================================================
# SAHIFA VIEW'LARI — Template (HTML)
# =============================================================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('build:home')

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                next_url = request.GET.get('next', 'build:home')
                return redirect(next_url)
            else:
                messages.error(request, "Akkaunt faol emas.")
        else:
            messages.error(request, "Username yoki parol noto'g'ri!")

    return render(request, 'accounts/login.html', {'form': form})


def step1_register_view(request):
    if request.user.is_authenticated:
        return redirect('build:home')
    
    if request.method == 'POST':
        role = request.POST.get('role', 'client')
        request.session['register_role'] = role
        return redirect('accounts:register')
        
    return render(request, 'accounts/step1_register.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('build:home')

    # Ensure step 1 was completed
    if 'register_role' not in request.session:
        return redirect('accounts:step1_register')

    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        from django.contrib.auth.models import User
        data = form.cleaned_data
        role = request.session.get('register_role', 'client')

        user = User.objects.create_user(
            username=data['username'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            email=data.get('email', ''),
            password=data['password'],
        )
        Profile.objects.filter(user=user).update(role=role)

        if role in ['builder', 'team']:
            profile = Profile.objects.get(user=user)
            profession = 'Kompaniya/Jamoa' if role == 'team' else 'Usta'
            BuilderProfile.objects.get_or_create(
                profile=profile,
                defaults={'profession': profession, 'experience_years': 0}
            )

        # Clear session
        if 'register_role' in request.session:
            del request.session['register_role']

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, user)
        messages.success(request, "Xush kelibsiz! Profilingizni to'ldiring.")
        return redirect('accounts:second_register')

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def second_register_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileEditForm(request.POST or None, request.FILES or None, instance=profile)

    if request.method == 'POST' and form.is_valid():
        form.save()
        if profile.role in ['builder', 'team']:
            profession = 'Kompaniya/Jamoa' if profile.role == 'team' else 'Usta'
            BuilderProfile.objects.get_or_create(
                profile=profile,
                defaults={'profession': profession, 'experience_years': 0}
            )
        messages.success(request, "Profil muvaffaqiyatli to'ldirildi!")
        return redirect('build:home')

    return render(request, 'accounts/second_register.html', {'form': form, 'profile': profile})


def logout_view(request):
    auth_logout(request)
    return redirect('build:home')