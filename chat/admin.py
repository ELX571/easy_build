from django.contrib import admin
from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'created_at')
    list_filter = ('created_at',)
    filter_horizontal = ('participants',)

    def get_participants(self, obj):
        return ', '.join(u.username for u in obj.participants.all())
    get_participants.short_description = 'Ishtirokchilar'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'sender', 'content_preview', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'room')
    search_fields = ('content', 'sender__username')
    readonly_fields = ('created_at',)

    def content_preview(self, obj):
        return obj.content[:60] + '...' if len(obj.content) > 60 else obj.content
    content_preview.short_description = 'Xabar'
