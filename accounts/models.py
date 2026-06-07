from django.db import models
from django.contrib.auth.models import User


class Role(models.Model):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('builder', 'Builder'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(

        upload_to='avatars/',
        default='avatars/default.png',
        blank=True,

                               )


