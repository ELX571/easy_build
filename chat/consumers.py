import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.cache import cache

from .models import ChatRoom, Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Real-time WebSocket Consumer for Chat and WebRTC.
    URL: /ws/chat/<room_id>/
    """

    # ── Online Status Management ───────────────────────────────────────────────

    @database_sync_to_async
    def set_online_status(self, is_online):
        """
        Manages user online status using a counter in the cache to support multiple tabs.
        Returns True if the global online/offline status actually changed.
        """
        key = f'user_online_{self.user.id}'
        count = cache.get(key, 0)
        
        if is_online:
            cache.set(key, count + 1, timeout=86400)
            return count == 0  # Status changed from offline to online
        else:
            if count <= 1:
                cache.delete(key)
                return True    # Status changed from online to offline
            else:
                cache.set(key, count - 1, timeout=86400)
                return False   # Status remains online

    @database_sync_to_async
    def get_all_room_groups_for_user(self):
        """Fetches all chat group names the user is a part of."""
        rooms = ChatRoom.objects.filter(participants=self.user)
        return [f'chat_{r.id}' for r in rooms]

    async def broadcast_status(self, is_online):
        """Broadcasts user online status to all rooms they are in."""
        groups = await self.get_all_room_groups_for_user()
        for group in groups:
            await self.channel_layer.group_send(group, {
                'type': 'user_status_change',
                'user_id': self.user.id,
                'is_online': is_online
            })

    # ── Connection Lifecycle ─────────────────────────────────────────────────

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close(code=4001)
            return

        changed = await self.set_online_status(True)
        await self.accept()

        self.subscribed_groups = []

        if self.room_id == '0':
            # Subscribe to all user rooms for global notifications
            rooms = await self.get_user_rooms(self.user)
            for room in rooms:
                g = f'chat_{room.id}'
                self.subscribed_groups.append(g)
                await self.channel_layer.group_add(g, self.channel_name)
            
            g_user = f'user_{self.user.id}'
            self.subscribed_groups.append(g_user)
            await self.channel_layer.group_add(g_user, self.channel_name)
        else:
            # Subscribe to a specific room only
            has_access = await self.user_has_access(self.room_id, self.user)
            if not has_access:
                await self.close(code=4003)
                return
            g = f'chat_{self.room_id}'
            self.subscribed_groups.append(g)
            await self.channel_layer.group_add(g, self.channel_name)

        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'room_id': int(self.room_id) if self.room_id != '0' else 0,
            'user_id': self.user.id,
        }))
        
        if changed:
            await self.broadcast_status(True)

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user.is_authenticated:
            changed = await self.set_online_status(False)
            if changed:
                await self.broadcast_status(False)
            
        if hasattr(self, 'subscribed_groups'):
            for g in self.subscribed_groups:
                await self.channel_layer.group_discard(g, self.channel_name)

    # ── Incoming Message Handling ────────────────────────────────────────────

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = data.get('type', 'message')
        room_id = str(data.get('room_id')) if self.room_id == '0' else self.room_id
        
        if not room_id or room_id == 'None':
            return

        room_group_name = f'chat_{room_id}'

        if msg_type == 'message':
            await self._handle_chat_message(data, room_id, room_group_name)

        elif msg_type == 'read_receipt':
            await self._handle_read_receipt(room_id, room_group_name)

        elif msg_type == 'typing':
            await self._handle_typing(data, room_id, room_group_name)

        elif msg_type == 'delete_message':
            await self._handle_delete_message(data, room_id, room_group_name)

        elif msg_type == 'edit_message':
            await self._handle_edit_message(data, room_id, room_group_name)

        elif msg_type == 'call_start':
            await self._handle_call_start(data, room_id, room_group_name)
            
        elif msg_type in ['call_answer', 'call_reject', 'call_end']:
            await self._handle_call_signal(msg_type, room_id, room_group_name)
            
        elif msg_type in ['webrtc_offer', 'webrtc_answer', 'webrtc_ice']:
            await self._handle_webrtc_signal(msg_type, data, room_id, room_group_name)

    # ── Handlers for Specific Actions ────────────────────────────────────────

    async def _handle_chat_message(self, data, room_id, group_name):
        content = data.get('message', '').strip()
        if not content:
            return

        message = await self.save_message(room_id, self.user, content)
        sender_name, sender_avatar = await self.get_sender_info(self.user)

        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'chat_message',
                'message_id': message.id,
                'message': content,
                'sender_id': self.user.id,
                'sender_name': sender_name,
                'sender_avatar': sender_avatar,
                'time': message.time_str(),
                'is_read': False,
                'room_id': int(room_id),
            }
        )

    async def _handle_read_receipt(self, room_id, group_name):
        count = await self.mark_messages_read(room_id, self.user)
        if count > 0:
            await self.channel_layer.group_send(
                group_name,
                {
                    'type': 'messages_read',
                    'reader_id': self.user.id,
                    'room_id': int(room_id),
                }
            )

    async def _handle_typing(self, data, room_id, group_name):
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'user_typing',
                'user_id': self.user.id,
                'is_typing': data.get('is_typing', False),
                'room_id': int(room_id)
            }
        )

    async def _handle_delete_message(self, data, room_id, group_name):
        message_id = data.get('message_id')
        if message_id:
            deleted = await self.delete_message_db(message_id, self.user)
            if deleted:
                await self.channel_layer.group_send(
                    group_name,
                    {
                        'type': 'message_deleted',
                        'message_id': message_id,
                        'room_id': int(room_id)
                    }
                )

    async def _handle_edit_message(self, data, room_id, group_name):
        message_id = data.get('message_id')
        new_content = data.get('new_content', '').strip()
        if message_id and new_content:
            edited = await self.edit_message_db(message_id, self.user, new_content)
            if edited:
                await self.channel_layer.group_send(
                    group_name,
                    {
                        'type': 'message_edited',
                        'message_id': message_id,
                        'new_content': new_content,
                        'room_id': int(room_id)
                    }
                )

    async def _handle_call_start(self, data, room_id, group_name):
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'call_incoming',
                'caller_id': self.user.id,
                'caller_name': self.user.get_full_name() or self.user.username,
                'call_type': data.get('call_type', 'video'),
                'room_id': int(room_id)
            }
        )

    async def _handle_call_signal(self, signal_type, room_id, group_name):
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'call_signal',
                'signal_type': signal_type,
                'user_id': self.user.id,
                'room_id': int(room_id)
            }
        )

    async def _handle_webrtc_signal(self, signal_type, data, room_id, group_name):
        target_id = data.get('target_id')
        payload = {
            'type': 'webrtc_signal',
            'signal_type': signal_type,
            'sender_id': self.user.id,
            'sdp': data.get('sdp'),
            'candidate': data.get('candidate'),
            'target_id': target_id,
            'room_id': int(room_id)
        }
        await self.channel_layer.group_send(group_name, payload)

    # ── Broadcast Event Transmitters ─────────────────────────────────────────

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_avatar': event.get('sender_avatar'),
            'time': event['time'],
            'is_read': event['is_read'],
            'file_url': event.get('file_url'),
            'file_type': event.get('file_type'),
            'room_id': event.get('room_id')
        }))

    async def messages_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'reader_id': event['reader_id'],
            'room_id': event['room_id'],
        }))

    async def user_typing(self, event):
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'is_typing': event['is_typing'],
                'room_id': event.get('room_id')
            }))

    async def user_status_change(self, event):
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_status',
                'user_id': event['user_id'],
                'is_online': event['is_online']
            }))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id'],
            'room_id': event.get('room_id')
        }))

    async def message_edited(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_edited',
            'message_id': event['message_id'],
            'new_content': event['new_content'],
            'room_id': event.get('room_id')
        }))

    async def call_incoming(self, event):
        if event['caller_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'call_incoming',
                'caller_id': event['caller_id'],
                'caller_name': event['caller_name'],
                'call_type': event['call_type'],
                'room_id': event['room_id']
            }))

    async def call_signal(self, event):
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': event['signal_type'],
                'user_id': event['user_id'],
                'room_id': event['room_id']
            }))

    async def webrtc_signal(self, event):
        target_id = event.get('target_id')
        if target_id and target_id != self.user.id:
            return
            
        if event['sender_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': event['signal_type'],
                'sender_id': event['sender_id'],
                'sdp': event.get('sdp'),
                'candidate': event.get('candidate'),
                'room_id': event.get('room_id')
            }))

    # ── Database Helpers ─────────────────────────────────────────────────────

    @database_sync_to_async
    def get_user_rooms(self, user):
        return list(ChatRoom.objects.filter(participants=user))

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
        return Message.objects.filter(
            room_id=room_id,
            is_read=False,
        ).exclude(sender=user).update(is_read=True)

    @database_sync_to_async
    def delete_message_db(self, message_id, user):
        try:
            msg = Message.objects.get(id=message_id, sender=user)
            msg.delete()
            return True
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def edit_message_db(self, message_id, user, new_content):
        try:
            msg = Message.objects.get(id=message_id, sender=user)
            msg.content = new_content
            msg.save(update_fields=['content'])
            return True
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def get_sender_info(self, user):
        name = user.get_full_name() or user.username
        avatar = None
        try:
            if hasattr(user, 'profile') and user.profile.avatar:
                avatar = user.profile.avatar.url
        except Exception:
            pass
        return name, avatar
