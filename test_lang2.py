import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
django.setup()
from django.test import Client

c = Client(enforce_csrf_checks=False)

# POST to set_language
res2 = c.post('/i18n/setlang/', {
    'language': 'ru',
    'next': '/uz/profile/edit/',
})

print("Status:", res2.status_code)
if res2.status_code == 302:
    print("Redirect URL:", res2.url)
    print("Language Cookie:", c.cookies.get('django_language').value if 'django_language' in c.cookies else 'None')

    # Follow the redirect!
    res3 = c.get(res2.url)
    print("Final Language from Context:", getattr(res3, 'context', {}).get('LANGUAGE_CODE', 'No Context'))
else:
    print("Content:", res2.content[:200])
