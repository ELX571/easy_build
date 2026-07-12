from accounts.models import Notification


def notifications_processor(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_notifications_count': unread_count}
    return {}


def subscription_processor(request):
    """
    Barcha shablonlarda obuna ma'lumotlarini taqdim etadi:
      - sub_is_premium     : bool
      - sub_plan_type      : 'free' | 'standard' | 'pro'
      - sub_plan_name      : str
      - sub_days_remaining : int | None
      - sub_is_active      : bool
      - sub_is_temp        : bool
    """
    if not request.user.is_authenticated:
        return {
            'sub_is_premium': False,
            'sub_plan_type': 'free',
            'sub_plan_name': None,
            'sub_days_remaining': None,
            'sub_is_active': False,
            'sub_is_temp': False,
        }

    try:
        profile = request.user.profile
        bp = getattr(profile, 'builder_info', None)

        return {
            'sub_is_premium': profile.is_premium,
            'sub_plan_type': bp.plan_type if bp else 'free',
            'sub_plan_name': bp.subscription_plan.name if (bp and bp.subscription_plan) else None,
            'sub_days_remaining': bp.days_remaining if bp else None,
            'sub_is_active': bp.has_active_subscription if bp else False,
            'sub_is_temp': (bp.is_temp_active and not bp.subscription_status) if bp else False,
        }
    except Exception:
        return {
            'sub_is_premium': False,
            'sub_plan_type': 'free',
            'sub_plan_name': None,
            'sub_days_remaining': None,
            'sub_is_active': False,
            'sub_is_temp': False,
        }
