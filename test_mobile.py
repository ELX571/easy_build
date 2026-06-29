import urllib.request
import re

req = urllib.request.Request('http://127.0.0.1:8000/uz/')
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    print("HTML fetched.")
except Exception as e:
    print(f"Error fetching HTML: {e}")
