from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accounts import views

app_name = 'accounts'

router = DefaultRouter()
router.register(r'auth', views.AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]

