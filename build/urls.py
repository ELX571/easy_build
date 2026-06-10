from django.urls import path
from build import views

app_name = 'build'

urlpatterns = [
    # Asosiy sahifa - Bosh sahifaga kirganda PostListView ishlaydi
    path('', views.PostListView.as_view(), name='home'),

    # ⚡️ SHABLONDAGI XATONI TUZATISH UCHUN: xuddi shu viewga 'post_list' nomini ham ulaymiz
    path('posts/', views.PostListView.as_view(), name='post_list'),

    # Usta profili linki

    # Profil linklari
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),

path('market/create/', views.post_create_view, name='post_create'),
]