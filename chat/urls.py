from django.urls import path
from chat import views

app_name = 'chat'

urlpatterns = [
    # ── Sahifa ──────────────────────────────────────────────────────────────────
    path('', views.chat_view, name='chat'),

    # ── REST API ────────────────────────────────────────────────────────────────
    path('api/contacts/', views.api_contacts, name='api_contacts'),
    path('api/messages/<int:room_id>/', views.api_messages, name='api_messages'),
    path('api/start/', views.api_start_chat, name='api_start'),
    path('api/users/', views.api_users, name='api_users'),
    path('api/unread/', views.api_unread_total, name='api_unread'),
    path('api/group/<int:room_id>/update/', views.api_update_group, name='api_update_group'),
]
