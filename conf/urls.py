from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.http import HttpResponse

# 1. TIL PREFIKSIZ (Sof marshrutlar)
# Bular global marshrutlar bo'lib, URL boshida /uz/, /ru/ prefikslarini talab qilmaydi
urlpatterns = [
    path('ping/', lambda request: HttpResponse('ok', status=200)),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),  # <── Eng tepaga chiqdi! Endi 404 mutlaqo bo'lmaydi.
]

# 2. TIL PREFIKSLI MARSHRUTLAR (i18n_patterns ichida)
# Hamma foydalanuvchi ko'radigan sahifalar shu yerga tushadi, shunda URL /uz/, /ru/, /en/ bilan ochiladi
urlpatterns += i18n_patterns(
    # ── Accounts & Auth ──
    path('accounts/', include('accounts.urls')),
    path('social/', include('allauth.urls')),

    # ── Chat ──
    path('chat/', include('chat.urls')),

    # ── Build (Bosh sahifa va Market Pro) ──
    # Bo'sh pattern ('') har doim i18n_patterns ichida ham eng oxirida turishi kerak
    path('', include('build.urls')),
)

# 3. DEVELOPMENT STILLAR VA MEDIA FAYLLAR
if settings.DEBUG:
    urlpatterns += [
        path('__reload__/', include('django_browser_reload.urls')),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)