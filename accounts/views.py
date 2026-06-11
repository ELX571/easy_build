from django.contrib.auth import logout as auth_logout, login
from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from accounts.models import Profile
from accounts.serializers import (
    UserLoginSerializer,
    UserRegisterSerializer,
    UserSecondRegisterSerializer,
)
from build.models import BuilderProfile


class AuthViewSet(viewsets.GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = UserLoginSerializer

    def get_permissions(self):
        return [AllowAny()]

    # ── LOGIN: GET → sahifa, POST → API ───────────────────────────────────────
    @action(methods=['get', 'post'], detail=False, url_path='login', url_name='login')
    def login_user(self, request):
        if request.method == 'GET':
            if request.user.is_authenticated:
                return redirect('/')
            return render(request, 'accounts/login.html')

        # POST
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response({'detail': 'Muvaffaqiyatli kirdingiz!'}, status=status.HTTP_200_OK)

    # ── REGISTER: GET → sahifa, POST → API ────────────────────────────────────
    @action(methods=['get', 'post'], detail=False, url_path='register', url_name='register')
    def register_user(self, request):
        if request.method == 'GET':
            if request.user.is_authenticated:
                return redirect('/')
            return render(request, 'accounts/register.html')

        # POST
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response(
            {'detail': "Ro'yxatdan o'tdingiz! Endi profilingizni to'ldiring."},
            status=status.HTTP_201_CREATED
        )

    # ── SECOND REGISTER: GET → sahifa, POST → API ─────────────────────────────
    @action(methods=['get', 'post'], detail=False, url_path='second-register', url_name='second-register')
    def register_second_user(self, request):
        if request.method == 'GET':
            if not request.user.is_authenticated:
                return redirect('/accounts/auth/login/')
            return render(request, 'accounts/second_register.html')

        # POST
        if not request.user.is_authenticated:
            return Response({'detail': "Avval ro'yxatdan o'ting."}, status=status.HTTP_401_UNAUTHORIZED)

        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = UserSecondRegisterSerializer(instance=profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_profile = serializer.save()

        if updated_profile.role == 'builder':
            BuilderProfile.objects.get_or_create(
                profile=updated_profile,
                defaults={'profession': 'Usta', 'experience_years': 0}
            )

        return Response({'detail': "Profil muvaffaqiyatli to'ldirildi!"}, status=status.HTTP_200_OK)

    # ── LOGOUT: POST ──────
    @action(methods=['post'], detail=False, url_path='logout', url_name='logout')
    def logout_user(self, request):
        auth_logout(request)
        return Response({'detail': 'Tizimdan chiqdingiz.'}, status=status.HTTP_200_OK)