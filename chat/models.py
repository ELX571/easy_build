from django.db import models
from build.models import BuilderProfile  # Modelni to'g'ridan-to'g'ri import qilamiz
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatRoom(models.Model):
    participants = models.ManyToManyField(
        User,
        related_name='chat_rooms',
        blank=True,
    )
    is_group = models.BooleanField(default=False)
    group_name = models.CharField(max_length=255, blank=True, null=True)
    group_avatar = models.ImageField(upload_to='group_avatars/', blank=True, null=True)
    team_profile = models.OneToOneField(
        'build.BuilderProfile', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='group_chat'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Chat Xonasi'
        verbose_name_plural = 'Chat Xonalari'
        ordering = ['-created_at']

    def __str__(self):
        names = ', '.join(u.get_full_name() or u.username for u in self.participants.all())
        return f"Room #{self.pk} — {names}"

    @classmethod
    def get_or_create_for(cls, user1, user2):
        rooms = cls.objects.filter(is_group=False, participants=user1).filter(participants=user2)
        for room in rooms:
            if room.participants.count() == 2:
                return room, False
        room = cls.objects.create(is_group=False)
        room.participants.add(user1, user2)
        return room, True

    def get_last_message(self):
        return self.messages.order_by('-created_at').first()

    def unread_count_for(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
    )
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    file_type = models.CharField(max_length=20, blank=True, null=True) # 'image', 'video', 'audio', 'document'
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Xabar'
        verbose_name_plural = 'Xabarlar'
        ordering = ['created_at']

    def __str__(self):
        return f"[Room#{self.room_id}] {self.sender.username}: {self.content[:50]}"

    def time_str(self):
        from django.utils import timezone
        import datetime
        now = timezone.now()
        created = self.created_at
        if not timezone.is_aware(created):
            created = timezone.make_aware(created)
        delta = now.date() - created.date()
        if delta.days == 0:
            return created.strftime('%H:%M')
        elif delta.days == 1:
            return 'Kecha'
        elif delta.days < 7:
            days = ['Dush', 'Sesh', 'Chor', 'Pay', 'Jum', 'Shan', 'Yak']
            return days[created.weekday()]
        else:
            return created.strftime('%d.%m')

    def to_dict(self, request=None):
        sender = self.sender
        avatar_url = None
        if hasattr(sender, 'profile'):
            if request:
                avatar_url = request.build_absolute_uri(sender.profile.get_avatar_url())
            else:
                avatar_url = sender.profile.get_avatar_url()

        return {
            'id': self.pk,
            'room_id': self.room_id,
            'sender_id': sender.pk,
            'sender_name': sender.get_full_name() or sender.username,
            'sender_avatar': avatar_url,
            'content': self.content or '',
            'file_url': request.build_absolute_uri(self.file.url) if (self.file and request) else (self.file.url if self.file else None),
            'file_type': self.file_type,
            'time': self.time_str(),
            'is_read': self.is_read,
        }


# chat/models.py ichida
team_profile = models.ForeignKey(
    'build.BuilderProfile',  # <-- Aynan shu ko'rinishda (Katta 'B' va 'P' harflari bilan)
    on_delete=models.SET_NULL,
    null=True,
    blank=True
)
