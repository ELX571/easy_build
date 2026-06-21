from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    ROLE_CHOICES = (
        ('client', 'Buyurtmachi (Mijoz)'),
        ('builder', 'Quruvchi (Usta)'),
        ('team', 'Qurilish jamoasi'),
    )

    REGION_CHOICES = (
        ('tashkent_sh', 'Toshkent shahri'),
        ('tashkent_v', 'Toshkent viloyati'),
        ('andijan', 'Andijon viloyati'),
        ('bukhara', 'Buxoro viloyati'),
        ('fergana', 'Farg\'ona viloyati'),
        ('jizzakh', 'Jizzax viloyati'),
        ('namangan', 'Namangan viloyati'),
        ('navoiy', 'Navoiy viloyati'),
        ('kashkadarya', 'Qashqadaryo viloyati'),
        ('samarkand', 'Samarkand viloyati'),
        ('sirdaryo', 'Sirdaryo viloyati'),
        ('surxondaryo', 'Surxondaryo viloyati'),
        ('khorezm', 'Xorazm viloyati'),
        ('karakalpakstan', 'Qoraqalpog\'iston Respublikasi'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=50, choices=REGION_CHOICES, default='tashkent_sh')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    telegram = models.CharField(max_length=100, blank=True, null=True, help_text="@username yoki t.me/username")
    whatsapp = models.CharField(max_length=20, blank=True, null=True, help_text="Xalqaro formatda: +998901234567")
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()}"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default_avatar.svg'
