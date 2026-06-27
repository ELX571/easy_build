from django.urls import path
from build import views
from build.views import workflow_list_view

app_name = 'build'

urlpatterns = [
    # ── Bosh sahifa ────────────────────────────────────────────────────────────
    path('', views.HomeView.as_view(), name='home'),
    
    # ── Tarmoq (Hamkasblar/O'xshash rollar) ──────────────────────────────────
    path('network/', views.NetworkView.as_view(), name='network'),

    # ── Usta Qidirish ──────────────────────────────────────────────────────────
    path('builders/', views.builder_list_view, name='builder_list'),

    # ── Market ─────────────────────────────────────────────────────────────────
    path('posts/', views.PostListView.as_view(), name='post_list'),

    path('workflow', workflow_list_view, name='workflow'),
    
    path('post/create/', views.post_create_view, name='post_create'),
    path('api/post/create/', views.PostCreateAPIView.as_view(), name='api_post_create'),
    path('api/post/<int:post_id>/like/', views.TogglePostLikeAPIView.as_view(), name='api_post_like'),
    path('api/post/<int:post_id>/bookmark/', views.TogglePostBookmarkAPIView.as_view(), name='api_post_bookmark'),
    path('api/user/<int:user_id>/contact/', views.UserContactInfoAPIView.as_view(), name='api_user_contact'),

    # ── Profil ─────────────────────────────────────────────────────────────────
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),

    # ── Team Management ────────────────────────────────────────────────────────
    path('api/team/search/', views.SearchUsersAPIView.as_view(), name='api_team_search'),
    path('api/team/add/<int:user_id>/', views.AddTeamMemberAPIView.as_view(), name='api_team_add'),
    path('api/team/remove/<int:user_id>/', views.RemoveTeamMemberAPIView.as_view(), name='api_team_remove'),
    path('api/team/invite/<int:invite_id>/', views.RespondTeamInviteAPIView.as_view(), name='api_team_invite'),

    path('post/<int:post_id>/edit/', views.post_edit_view, name='post_edit'),
    path('post/<int:post_id>/delete/', views.post_delete_view, name='post_delete'),
]