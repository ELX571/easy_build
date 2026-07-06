from django.apps import AppConfig


class BuildConfig(AppConfig):
    name = 'build'

    def ready(self):
        import os
        from django.conf import settings
        
        # Prevent running thread twice in dev (runserver starts 2 processes by default)
        if os.environ.get('RUN_MAIN', None) == 'true' or not settings.DEBUG:
            from .keep_alive import start_keep_alive
            # Render URL to keep the app awake
            start_keep_alive('https://easy-build-bmz2.onrender.com/ping/')
