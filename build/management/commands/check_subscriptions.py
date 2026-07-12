"""
EasyBuild — Management Command: check_subscriptions
Obunalarni tekshirib, muddati o'tganlarini avtomatik o'chiradi.

Ishlatish:
    python manage.py check_subscriptions

Cron uchun (har kecha soat 00:00 da):
    0 0 * * * /path/to/venv/bin/python /path/to/manage.py check_subscriptions
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction


class Command(BaseCommand):
    help = "Muddati o'tgan obunalarni tekshirib, is_premium ni o'chiradi."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Haqiqatda o'zgartirmasdan faqat ko'rsatadi.",
        )

    def handle(self, *args, **options):
        from build.models import BuilderProfile
        from accounts.models import Notification

        dry_run = options['dry_run']
        now = timezone.now()
        expired_count = 0
        warning_count = 0

        # 1️⃣  Muddati o'tgan obunalar
        expired_profiles = BuilderProfile.objects.filter(
            subscription_status=True,
            subscription_end__isnull=False,
            subscription_end__lt=now,
        ).select_related('profile__user', 'subscription_plan')

        for bp in expired_profiles:
            user = bp.profile.user
            plan_name = bp.subscription_plan.name if bp.subscription_plan else "Noma'lum"

            self.stdout.write(
                self.style.WARNING(
                    f"⏰ Muddati o'tgan: {user.username} | Plan: {plan_name} | "
                    f"Tugagan: {bp.subscription_end.strftime('%Y-%m-%d')}"
                )
            )

            if not dry_run:
                with transaction.atomic():
                    bp.subscription_status = False
                    bp.subscription_plan = None
                    bp.save(update_fields=['subscription_status', 'subscription_plan'])

                    # is_premium ni o'chirish (signal ham qiladi lekin ishonch uchun)
                    bp.profile.is_premium = False
                    bp.profile.save(update_fields=['is_premium'])

                    # Foydalanuvchiga bildirishnoma
                    Notification.objects.create(
                        user=user,
                        title="⚠️ Obuna muddati tugadi",
                        message=(
                            f"Sizning '{plan_name}' obunangiz muddati tugadi. "
                            "Platformaning to'liq imkoniyatlaridan foydalanishni davom ettirish uchun "
                            "obunangizni yangilang."
                        ),
                        icon='fa-solid fa-clock',
                        url='/uz/payment-dashboard/',
                    )

            expired_count += 1

        # 2️⃣  7 kundan kam qolgan obunalar — eslatma
        warning_deadline = now + timezone.timedelta(days=7)
        expiring_soon = BuilderProfile.objects.filter(
            subscription_status=True,
            subscription_end__isnull=False,
            subscription_end__gt=now,
            subscription_end__lt=warning_deadline,
        ).select_related('profile__user', 'subscription_plan')

        for bp in expiring_soon:
            user = bp.profile.user
            plan_name = bp.subscription_plan.name if bp.subscription_plan else "Noma'lum"
            days_left = (bp.subscription_end - now).days

            self.stdout.write(
                self.style.NOTICE(
                    f"⏳ Tugayapti: {user.username} | Plan: {plan_name} | "
                    f"{days_left} kun qoldi"
                )
            )

            if not dry_run:
                # Faqat bir marta eslatma yuboramiz (mavjudligini tekshiramiz)
                already_notified = user.notifications.filter(
                    title__contains="Obuna tugayapti",
                    created_at__gte=now - timezone.timedelta(days=1)
                ).exists()

                if not already_notified:
                    Notification.objects.create(
                        user=user,
                        title=f"⏳ Obuna {days_left} kun ichida tugaydi!",
                        message=(
                            f"Sizning '{plan_name}' obunangiz {days_left} kun ichida tugaydi. "
                            "Xizmatlardan uzliksiz foydalanish uchun vaqtida yangilang."
                        ),
                        icon='fa-solid fa-hourglass-half',
                        url='/uz/payment-dashboard/',
                    )

            warning_count += 1

        # Natija
        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"\n[DRY RUN] {expired_count} ta o'chirilar edi, {warning_count} ta eslatma yuborilardi."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Tugallandi: {expired_count} ta obuna o'chirildi, "
                f"{warning_count} ta eslatma yuborildi."
            ))