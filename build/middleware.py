from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render

SUBSCRIPTION_CHECK_INTERVAL_SECONDS = 900  # 15 daqiqa


class SubscriptionExpiryMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if not request.user.is_authenticated:
            return None

        session = request.session
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

            if (bp.subscription_status and
                    bp.subscription_end and
                    bp.subscription_end < timezone.now()):

                plan_name = bp.subscription_plan.name if bp.subscription_plan else "Obuna"
                bp.subscription_status = False
                bp.subscription_plan = None
                bp.save(update_fields=['subscription_status', 'subscription_plan'])

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

            elif (bp.is_temp_active and
                  bp.temp_active_until and
                  bp.temp_active_until < timezone.now()):

                bp.is_temp_active = False
                bp.save(update_fields=['is_temp_active'])

        except Exception:
            pass

        return None


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Superadmin "Maintenance Mode" (Texnik tanaffus) yoqqanida:
    Superuser'dan tashqari barcha oddiy foydalanuvchilar va mehmonlar uchun
    saytning har qanday sahifasiga kirish bloklanadi va chiroyli Maintenance sahifasi ko'rsatiladi.
    """
    def process_request(self, request):
        try:
            from build.models import SystemSetting
            setting = SystemSetting.get_settings()
            if not setting.maintenance_mode:
                return None

            # Superuser / staff holatida ruxsat beriladi
            if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
                return None

            # Admin va static resurslarga ruxsat beramiz
            path = request.path_info
            exempt_prefixes = [
                '/admin/', '/superadmin/', '/static/', '/media/', '/i18n/', '/accounts/login/'
            ]
            if any(path.startswith(prefix) for prefix in exempt_prefixes):
                return None

            from django.utils.translation import get_language
            lang = get_language() or 'uz'
            if lang == 'ru':
                msg = setting.maintenance_message_ru
            elif lang == 'en':
                msg = setting.maintenance_message_en
            else:
                msg = setting.maintenance_message_uz

            return render(request, 'maintenance.html', {
                'maintenance_message': msg,
                'setting': setting,
            }, status=503)
        except Exception:
            return None


class AuditLogMiddleware(MiddlewareMixin):
    """
    Real-time foydalanuvchilar oqimi va trafik loglarini bazaga yozuvchi middleware.
    """
    def process_response(self, request, response):
        try:
            path = request.path_info
            if any(path.startswith(p) for p in ['/static/', '/media/', '/favicon.ico']):
                return response

            from build.models import TrafficLog
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR', '')

            user = request.user if request.user.is_authenticated else None
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:490]

            TrafficLog.objects.create(
                user=user,
                ip_address=ip[:45],
                path=path[:490],
                method=request.method[:10],
                user_agent=user_agent,
                status_code=response.status_code
            )
        except Exception:
            pass

        return response
