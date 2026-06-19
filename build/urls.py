from django.urls import path
from build import views

app_name = 'build'

urlpatterns = [
    # Bosh sahifa
    path('', views.PostListView.as_view(), name='home'),

    # Market
    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('market/create/', views.post_create_view, name='post_create'),

    # Profil
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
]