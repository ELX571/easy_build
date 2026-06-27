from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp


class SiteFallbackSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Google OAuth uchun adapter.
    DB dagi socialaccount_socialapp jadvalidan o'qiydi.
    Sayt bilan bog'liq muammo bo'lsa, barcha saytlar uchun fallback qiladi.
    """
    def get_app(self, request, provider, client_id=None):
        try:
            # Avval odatiy yo'l bilan (sayt bo'yicha) izlaymiz
            return super().get_app(request, provider, client_id=client_id)
        except SocialApp.DoesNotExist:
            # Agar sayt bo'yicha topilmasa, barcha saytlardagini olamiz
            apps = SocialApp.objects.filter(
                Q(provider=provider) | Q(provider_id=provider)
            )
            if client_id:
                apps = apps.filter(client_id=client_id)

            visible_apps = [app for app in apps if not app.settings.get("hidden")]

            if len(visible_apps) == 1:
                return visible_apps[0]
            if len(visible_apps) > 1:
                raise MultipleObjectsReturned
            raise
