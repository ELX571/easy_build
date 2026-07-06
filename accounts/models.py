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

    # --- Notification Settings ---
    notify_messages = models.BooleanField(default=True, verbose_name=_("Yangi xabarlar"))
    notify_orders = models.BooleanField(default=True, verbose_name=_("Yangi buyurtmalar"))
    notify_system = models.BooleanField(default=True, verbose_name=_("Tizim xabarnomalari"))
    notify_promotions = models.BooleanField(default=False, verbose_name=_("Aksiya va chegirmalar"))

    # --- Trust Index (Ishonch Indeksi) Fields ---
    is_verified = models.BooleanField(default=True, verbose_name=_("Tasdiqlangan usta")) # Default true for blue checkmark
    is_premium = models.BooleanField(default=False, verbose_name=_("Premium obunachi"))
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name=_("O'rtacha baho"))
    completed_orders_count = models.PositiveIntegerField(default=0, verbose_name=_("Tugatilgan buyurtmalar"))
    canceled_orders_count = models.PositiveIntegerField(default=0, verbose_name=_("Bekor qilingan buyurtmalar"))
    response_time_minutes = models.PositiveIntegerField(default=0, help_text=_("O'rtacha javob berish vaqti (daqiqa)"))

    @property
    def trust_index(self):
        score = 0.0
        
        # 1. Mijoz Bahosi (50%)
        score += float(self.rating_average) * 10.0
        
        # 2. Platforma Obro'si (30%)
        if self.is_verified:
            score += 15.0
            
        completeness = 0
        if self.avatar: completeness += 3
        if self.bio: completeness += 3
        if self.telegram or self.whatsapp or self.instagram or self.facebook: completeness += 4
        score += completeness
        
        delta = timezone.now() - self.created_at
        if delta.days >= 365:
            score += 5.0
        elif delta.days >= 180:
            score += 3.0
        elif delta.days >= 30:
            score += 2.0
            
        # 3. Javob tezligi va Sifat (20%)
        total_orders = self.completed_orders_count + self.canceled_orders_count
        if total_orders > 0:
            success_rate = self.completed_orders_count / total_orders
            score += success_rate * 10.0
        else:
            # Yangi ustalar uchun neutral ball
            score += 5.0
            
        if self.response_time_minutes == 0 or self.response_time_minutes <= 60:
            score += 10.0
        elif self.response_time_minutes <= 180:
            score += 7.0
        else:
            score += 2.0
            
        return min(round(score), 100)

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()}"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default_avatar.svg'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255, verbose_name=_("Sarlavha"))
    message = models.TextField(verbose_name=_("Xabar matni"))
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Havola (URL)"))
    icon = models.CharField(max_length=50, default='fa-solid fa-bell', blank=True, null=True)
    is_read = models.BooleanField(default=False, verbose_name=_("O'qilgan"))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username} - {self.title}"
