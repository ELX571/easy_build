"""
EasyBuild — Subscription Expiry Middleware
Har so'rovda (request) foydalanuvchining obuna muddatini tekshiradi.
Muddati o'tgan bo'lsa — avtomatik o'chiradi va bildirishnoma yuboradi.
Yengil ishlash uchun faqat autentifikatsiya qilingan ustalarda, har 15 daqiqada bir tekshiradi.
"""
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


SUBSCRIPTION_CHECK_INTERVAL_SECONDS = 900  # 15 daqiqa


class SubscriptionExpiryMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if not request.user.is_authenticated:
            return None

        session = request.session

        # 15 daqiqada bir marta tekshirish (har requestda DB ga urmaslik)
        last_check = session.get('sub_last_check')
        now_ts = timezone.now().timestamp()

        if last_check and (now_ts - last_check) < SUBSCRIPTION_CHECK_INTERVAL_SECONDS:
            return None

        session['sub_last_check'] = now_ts

        try:
            profile = request.user.profile
            bp = getattr(profile, 'builder_info', None)
            if not bp:
                return None

            # Muddati o'tganmi?
            if (bp.subscription_status and
                    bp.subscription_end and
                    bp.subscription_end < timezone.now()):

                plan_name = bp.subscription_plan.name if bp.subscription_plan else "Obuna"

                # Obunani o'chiramiz
                bp.subscription_status = False
                bp.subscription_plan = None
                bp.save(update_fields=['subscription_status', 'subscription_plan'])
                # Signals is_premium ni sinxronlaydi

                # Foydalanuvchiga bildirishnoma
                from accounts.models import Notification
                already_notified = profile.user.notifications.filter(
                    title__icontains='Obuna muddati tugadi',
                    created_at__gte=timezone.now() - timezone.timedelta(hours=24)
                ).exists()

                if not already_notified:
                    Notification.objects.create(
                        user=profile.user,
                        title="⚠️ Obuna muddati tugadi",
                        message=(
                            f"Sizning '{plan_name}' obunangiz muddati tugadi. "
                            "Platformaning to'liq imkoniyatlaridan foydalanishni davom ettirish uchun "
                            "obunangizni yangilang."
                        ),
                        icon='fa-solid fa-clock',
                        url='/uz/payment-dashboard/',
                    )

            # Temp obuna muddati o'tganmi?
            elif (bp.is_temp_active and
                  bp.temp_active_until and
                  bp.temp_active_until < timezone.now()):

                bp.is_temp_active = False
                bp.save(update_fields=['is_temp_active'])

        except Exception:
            pass  # Har qanday xatoda — davom etamiz

        return None
