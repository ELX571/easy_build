from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Profile, Role


@receiver(post_save, sender=User)
def create_user_related_models(sender, instance, created, **kwargs):
    if not created:
        return

    Profile.objects.get_or_create(user=instance, defaults={'username': instance.username})
    Role.objects.get_or_create(user=instance, defaults={'role': 'client'})
