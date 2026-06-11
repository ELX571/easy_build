
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    ROLE_CHOICES = (
        ('client', 'Buyurtmachi (Mijoz)'),
        ('builder', 'Quruvchi (Usta)'),
    )

    REGION_CHOICES = (
        ('tashkent_sh', 'Toshkent shahri'),
        ('tashkent_v', 'Toshkent viloyati'),
        ('andijan', 'Andijon viloyati'),
        ('bukhara', 'Buxoro viloyati'),
        ('fergana', 'Fargʻona viloyati'),
        ('jizzakh', 'Jizzax viloyati'),
        ('namangan', 'Namangan viloyati'),
        ('navoiy', 'Navoiy viloyati'),
        ('kashkadarya', 'Qashqadaryo viloyati'),
        ('samarkand', 'Samarkand viloyati'),
        ('sirdaryo', 'Sirdaryo viloyati'),
        ('surxondaryo', 'Surxondaryo viloyati'),
        ('khorezm', 'Xorazm viloyati'),
        ('karakalpakstan', 'Qoraqalpogʻiston Respublikasi'),
    )

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # ⚡️ Ustun o'zgartirildi: CharField endi tanlovli (choices) bo'ldi
    city = models.CharField(max_length=50, choices=REGION_CHOICES, default='tashkent_sh')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg', blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    # def __str__(self):
    #     return f"{self.user.username} - {self.get_role_display()}"
