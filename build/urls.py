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

    path('workflow/', workflow_list_view, name='workflow'),
    
    path('post/create/', views.post_create_view, name='post_create'),
    path('api/post/create/', views.PostCreateAPIView.as_view(), name='api_post_create'),
    path('api/post/<int:post_id>/like/', views.TogglePostLikeAPIView.as_view(), name='api_post_like'),
    path('api/post/<int:post_id>/bookmark/', views.TogglePostBookmarkAPIView.as_view(), name='api_post_bookmark'),
    path('api/user/<int:user_id>/contact/', views.UserContactInfoAPIView.as_view(), name='api_user_contact'),
    path('api/user/<int:user_id>/negotiate/', views.NegotiateAPIView.as_view(), name='api_user_negotiate'),
    path('api/user/<int:user_id>/interest/', views.ShowInterestAPIView.as_view(), name='api_user_interest'),
    path('api/notifications/read/', views.mark_notifications_read, name='api_notifications_read'),

    # ── Profil ─────────────────────────────────────────────────────────────────
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.profile_view, name='public_profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/verify/', views.verify_profile_view, name='profile_verify'),
    path('profile/notifications/', views.update_notifications_view, name='update_notifications'),
    path('notifications/', views.notifications_list_view, name='notifications_list'),

    # ── Team Management ────────────────────────────────────────────────────────
    path('api/team/search/', views.SearchUsersAPIView.as_view(), name='api_team_search'),
    path('api/team/add/<int:user_id>/', views.AddTeamMemberAPIView.as_view(), name='api_team_add'),
    path('api/team/remove/<int:user_id>/', views.RemoveTeamMemberAPIView.as_view(), name='api_team_remove'),
    path('api/team/invite/<int:invite_id>/', views.RespondTeamInviteAPIView.as_view(), name='api_team_invite'),
    path('api/team/update-name/', views.UpdateTeamNameAPIView.as_view(), name='api_team_update_name'),

    path('post/<int:post_id>/edit/', views.post_edit_view, name='post_edit'),
    path('post/<int:post_id>/delete/', views.post_delete_view, name='post_delete'),
    path('market/', views.market_pro_view, name='market'),
    path('order/<int:order_id>/review/', views.leave_review_view, name='leave_review'),
    path('plans/', views.plans_list, name='plans_list'),
    path('plans/<int:plan_id>/subscribe/', views.choose_plan, name='choose_plan'),
    path('verification/', views.admin_verification_dashboard, name='admin_verification_dashboard'),
    path('verification/<int:request_id>/<str:action>/', views.process_verification, name='process_verification'),
    path('verification/chat/<int:user_id>/', views.chat_room_redirect, name='chat_room_redirect'),
    path('payment-dashboard/', views.payment_dashboard, name='payment_dashboard'),
]
