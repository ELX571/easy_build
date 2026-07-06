import os
import glob

# The replacement block
replacement = """<a href="{% url 'build:notifications_list' %}" class="rail-item {% if request.resolver_match.url_name == 'notifications_list' %}active{% endif %}" data-title="Bildirishnomalar">
    <i class="fa-solid fa-bell"></i>
    {% if unread_notifications_count > 0 %}
        <span style="position:absolute; top:8px; right:8px; background:#ef4444; color:white; font-size:10px; font-weight:800; border-radius:50%; width:16px; height:16px; display:flex; align-items:center; justify-content:center; border:2px solid var(--bg-panel);">{{ unread_notifications_count }}</span>
    {% endif %}
</a>"""

import re

for filepath in glob.glob("templates/**/*.html", recursive=True):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # We want to replace the rail-item containing fa-gear that goes to profile_edit
    # Example: <a href="{% url 'build:profile_edit' %}" class="rail-item {% if request.resolver_match.url_name == 'profile_edit' %}active{% endif %}" data-title="Sozlamalar"><i class="fa-solid fa-gear"></i></a>
    
    # Regex to match the rail item
    pattern = re.compile(r'<a[^>]*href="\{%\s*url\s*\'build:profile_edit\'\s*%\}"[^>]*class="rail-item[^"]*"[^>]*>\s*<i[^>]*fa-gear[^>]*></i>\s*</a>')
    
    new_content = pattern.sub(replacement, content)
    
    # Check if there is another format (like in post_create or home where trans 'Sozlamalar' is used)
    pattern2 = re.compile(r'<a[^>]*href="\{%\s*url\s*\'build:profile_edit\'\s*%\}"[^>]*class="rail-item[^>]*>\s*<i class="fa-solid fa-gear"></i>\s*</a>')
    
    new_content = pattern2.sub(replacement, new_content)
    
    # One more for profile.html which has a different format maybe? Wait, profile.html doesn't have a rail-item with a gear. Oh, it does! 
    # Let's just blindly replace any rail-item with build:profile_edit and fa-gear inside.
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Replaced in {filepath}")
