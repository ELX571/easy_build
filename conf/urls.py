from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ── Admin ──────────────────────────────────────────────────────────────────
    path('admin/', admin.site.urls),

    # ── Accounts ───────────────────────────────────────────────────────────────
    path('accounts/', include('accounts.urls')),

    # ── Allauth (Google OAuth) ─────────────────────────────────────────────────
    path('social/', include('allauth.urls')),

    # ── Chat ───────────────────────────────────────────────────────────────────
    path('chat/', include('chat.urls')),

    # ── Build (bosh sahifa) ────────────────────────────────────────────────────
    path('', include('build.urls')),

    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += [
        path('__reload__/', include('django_browser_reload.urls')),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

