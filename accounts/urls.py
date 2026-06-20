from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from accounts import views

app_name = 'accounts'

router = DefaultRouter()
router.register(r'api', views.AuthViewSet, basename='auth')

urlpatterns = [
    # ── API (DRF) ──────────────────────────────────────────────────────────────
    path('', include(router.urls)),

    # ── Sahifalar ──────────────────────────────────────────────────────────────
    path('login/', views.login_view, name='login'),
    path('register/step-1/', views.step1_register_view, name='step1_register'),
    path('register/step-2/', views.register_view, name='register'),
    path('register/step-3/', views.second_register_view, name='second_register'),
    path('logout/', views.logout_view, name='logout'),

    # ── Eski linklarni qayta yo'naltirish (Fallback Redirects) ─────────────────
    # ── Eski linklarni qayta yo'naltirish (Fallback Redirects) ─────────────────
    path('auth/register/', RedirectView.as_view(pattern_name='accounts:register', permanent=False)),
    path('auth/login/', RedirectView.as_view(pattern_name='accounts:login', permanent=False)),
    path('auth/second-register/', RedirectView.as_view(pattern_name='accounts:second_register', permanent=False)),
]
