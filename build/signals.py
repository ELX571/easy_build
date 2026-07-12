"""
EasyBuild — Subscription Signals
Obuna holati o'zgarganda profile.is_premium ni avtomatik sinxronlashtiradi
va SubscriptionHistory'ga voqeani yozadi.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone


def _log_event(user, event, plan_name=None, note=None, performed_by=None):
    """SubscriptionHistory'ga xavfsiz yozish yordamchi funksiyasi."""
    try:
        from build.models import SubscriptionHistory
        SubscriptionHistory.objects.create(
            user=user,
            event=event,
            plan_name=plan_name,
            note=note,
            performed_by=performed_by,
        )
    except Exception:
        pass


@receiver(pre_save, sender='build.BuilderProfile')
def auto_expire_subscription(sender, instance, **kwargs):
    """
    Saqlashdan OLDIN: Muddati o'tgan obunani avtomatik o'chirish.
    """
    if (instance.subscription_status and
            instance.subscription_end and
            instance.subscription_end < timezone.now()):
        instance.subscription_status = False
        instance.subscription_plan_id = None  # FK clear
        # Note: plan_type will return 'free' after this


@receiver(post_save, sender='build.BuilderProfile')
def sync_premium_and_log(sender, instance, created, **kwargs):
    """
    Saqlangandan KEYIN:
    1. profile.is_premium ni sinxronlaydi
    2. Holat o'zgarishini SubscriptionHistory'ga yozadi
    """
    try:
        profile = instance.profile
        should_be_premium = instance.has_active_subscription

        # is_premium sinxronlash
        if profile.is_premium != should_be_premium:
            old_premium = profile.is_premium
            profile.is_premium = should_be_premium
            profile.save(update_fields=['is_premium'])

            # Tarixga yozish
            plan_name = (instance.subscription_plan.name
                         if instance.subscription_plan else None)

            if should_be_premium and not old_premium:
                plan_type = instance.plan_type
                event = 'pro_granted' if plan_type == 'pro' else (
                    'temp_activated' if instance.is_temp_active else 'activated'
                )
                _log_event(profile.user, event, plan_name=plan_name,
                           note="Avtomatik sinxronlash orqali faollashtirildi")
            elif not should_be_premium and old_premium:
                _log_event(profile.user, 'expired', plan_name=plan_name,
                           note="Muddati tugadi yoki bekor qilindi")

    except Exception:
        pass


@receiver(post_save, sender='build.SubscriptionRequest')
def notify_admin_on_new_request(sender, instance, created, **kwargs):
    """
    Yangi to'lov cheki yuborilganda:
    - Barcha adminlarga bildirishnoma
    - SubscriptionHistory'ga yoziladi
    """
    if not created:
        return

    try:
        from django.contrib.auth.models import User
        from accounts.models import Notification

        admins = User.objects.filter(is_staff=True)
        requester_name = instance.user.get_full_name() or instance.user.username

        for admin in admins:
            Notification.objects.create(
                user=admin,
                title="💳 Yangi to'lov cheki keldi!",
                message=(
                    f"{requester_name} '{instance.plan_name}' obunasi uchun "
                    f"{instance.amount} so'm miqdorida to'lov cheki yubordi. "
                    f"Iltimos, tasdiqlang yoki rad eting."
                ),
                icon='fa-solid fa-money-bill-wave',
                url='/uz/verification/',
            )

        # Tarixga yozish
        _log_event(
            instance.user,
            event='temp_activated',
            plan_name=instance.plan_name,
            note=f"To'lov cheki yuborildi. Miqdor: {instance.amount} so'm"
        )

    except Exception:
        pass
