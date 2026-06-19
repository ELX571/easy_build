import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Real-time WebSocket Consumer.
    URL: /ws/chat/<room_id>/
    """

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        # Autentifikatsiya tekshiruvi
        if not self.user.is_authenticated:
            await self.close(code=4001)
            return

        # Foydalanuvchi ushbu xonaga ruxsat bor-yo'qligini tekshirish
        if not await self.user_has_access(self.room_id, self.user):
            await self.close(code=4003)
            return

        # Channel group'ga qo'shish
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

        # Ulanish muvaffaqiyatli ekanini xabar qilish
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'room_id': self.room_id,
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

    async def receive(self, text_data):
        """Clientdan xabar kelganda."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = data.get('type', 'message')

        if msg_type == 'message':
            content = data.get('message', '').strip()
            if not content:
                return

            # DB ga saqlash
            message = await self.save_message(self.room_id, self.user, content)

            # Guruhga broadcast
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': message.id,
                    'message': content,
                    'sender_id': self.user.id,
                    'sender_name': self.user.get_full_name() or self.user.username,
                    'time': message.time_str(),
                    'is_read': False,
                }
            )

        elif msg_type == 'read_receipt':
            # O'qilgan xabarlarni belgilash
            await self.mark_messages_read(self.room_id, self.user)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'reader_id': self.user.id,
                }
            )

    # ── Group event handlers ──

    async def chat_message(self, event):
        """Guruhdan xabar kelib, clientga yuborish."""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'time': event['time'],
            'is_read': event['is_read'],
        }))

    async def messages_read(self, event):
        """O'qildi signalini clientga yuborish."""
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'reader_id': event['reader_id'],
        }))

    # ── DB helpers (sync → async) ──

    @database_sync_to_async
    def user_has_access(self, room_id, user):
        try:
            room = ChatRoom.objects.get(pk=room_id)
            return room.participants.filter(pk=user.pk).exists()
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, room_id, user, content):
        room = ChatRoom.objects.get(pk=room_id)
        return Message.objects.create(room=room, sender=user, content=content)

    @database_sync_to_async
    def mark_messages_read(self, room_id, user):
        Message.objects.filter(
            room_id=room_id,
            is_read=False,
        ).exclude(sender=user).update(is_read=True)
