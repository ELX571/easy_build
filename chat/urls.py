from django.urls import path
from chat import views

app_name = 'chat'

urlpatterns = [
    # ── Sahifalar ──
    path('', views.chat_view, name='chat'),
    path('room/<int:room_id>/', views.room_view, name='room'),

    # ── REST API ──
    path('api/contacts/', views.api_contacts, name='api_contacts'),
    path('api/room/<int:room_id>/messages/', views.api_messages, name='api_messages'),
    path('api/start/', views.api_start_chat, name='api_start_chat'),
    path('api/users/', views.api_users, name='api_users'),
]
