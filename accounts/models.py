from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    ROLE_CHOICES = (
        ('client', _('Buyurtmachi (Mijoz)')),
        ('builder', _('Quruvchi (Usta)')),
        ('team', _('Qurilish jamoasi')),
    )

    REGION_CHOICES = (
        ('tashkent_sh', _('Toshkent shahri')),
        ('tashkent_v', _('Toshkent viloyati')),
        ('andijan', _('Andijon viloyati')),
        ('bukhara', _('Buxoro viloyati')),
        ('fergana', _("Farg'ona viloyati")),
        ('jizzakh', _('Jizzax viloyati')),
        ('namangan', _('Namangan viloyati')),
        ('navoiy', _('Navoiy viloyati')),
        ('kashkadarya', _('Qashqadaryo viloyati')),
        ('samarkand', _('Samarkand viloyati')),
        ('sirdaryo', _('Sirdaryo viloyati')),
        ('surxondaryo', _('Surxondaryo viloyati')),
        ('khorezm', _('Xorazm viloyati')),
        ('karakalpakstan', _("Qoraqalpog'iston Respublikasi")),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=50, choices=REGION_CHOICES, default='tashkent_sh')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    telegram = models.CharField(max_length=100, blank=True, null=True, help_text="@username yoki t.me/username")
    whatsapp = models.CharField(max_length=20, blank=True, null=True, help_text="Xalqaro formatda: +998901234567")
    instagram = models.CharField(max_length=100, blank=True, null=True, help_text="@username yoki instagram profil linki")
    facebook = models.CharField(max_length=100, blank=True, null=True, help_text="Facebook profil linki yoki username")
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()}"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default_avatar.svg'
