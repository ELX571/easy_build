from django.urls import path

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('second-register/', views.second_register, name='second_register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]
