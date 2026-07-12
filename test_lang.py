import requests

session = requests.Session()
# First get the page to get CSRF token
response = session.get('http://127.0.0.1:8000/uz/profile/edit/')
csrf = session.cookies.get('csrftoken')

print("CSRF Token:", csrf)

# Now POST to set_language
res = session.post(
    'http://127.0.0.1:8000/i18n/setlang/',
    data={'language': 'ru', 'next': '/uz/profile/edit/', 'csrfmiddlewaretoken': csrf},
    headers={'Referer': 'http://127.0.0.1:8000/uz/profile/edit/'},
    allow_redirects=False
)

print("Status:", res.status_code)
print("Location:", res.headers.get('Location'))
print("Cookies:", session.cookies.get_dict())
