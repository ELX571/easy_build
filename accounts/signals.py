from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import Profile

@receiver(post_save, sender=User)
def create_user_related_models(sender, instance, created, **kwargs):
    if not created:
        return

    # User yaratilishi bilanoq unga tegishli Profile obyektini
    # bazada xatosiz va ortiqcha maydonlarsiz avtomatik yaratamiz
    Profile.objects.get_or_create(
        user=instance,
        defaults={'role': 'client'} # Default holatda hammaga 'client' (mijoz) roli beriladi
    )