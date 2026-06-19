from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatRoom(models.Model):
    """
    Ikki foydalanuvchi orasidagi yagona xususiy suhbat xonasi.
    participants M2M orqali saqlanadi, lekin har doim 2 ta user bo'ladi.
    """
    participants = models.ManyToManyField(
        User,
        related_name='chat_rooms',
        blank=True,
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
        """Ikki user uchun mavjud xonani topadi yoki yangi yaratadi."""
        # user1 va user2 ikkisini ham o'z ichiga olgan xonalar
        rooms = cls.objects.filter(participants=user1).filter(participants=user2)
        # Faqat 2 ta ishtirokchisi bo'lgan xona
        for room in rooms:
            if room.participants.count() == 2:
                return room, False
        room = cls.objects.create()
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
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Xabar'
        verbose_name_plural = 'Xabarlar'
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.room_id}] {self.sender.username}: {self.content[:40]}"

    def time_str(self):
        """HH:MM formatida vaqt qaytaradi."""
        return self.created_at.strftime('%H:%M')
