from django.urls import path

from account import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('second-register/', views.second_register, name='second_register'),
    path('login/', views.login, name='login'),
]