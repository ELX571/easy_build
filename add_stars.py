import glob
import re

rating_html = """ &middot; <span style="color:#f59e0b; font-weight:600; display:inline-flex; align-items:center; gap:3px;"><i class="fa-solid fa-star" style="font-size:11px;"></i> {{ post.author.profile.rating_average|floatformat:1 }}</span>"""

for file_path in ['templates/build/home.html', 'templates/build/network.html', 'templates/build/profile.html']:
    with open(file_path, 'r') as f:
        content = f.read()

    # Find where the username and time are
    # network.html: <div class="tweet-username">@{{ post.author.username }} &middot; {{ post.created_time|timesince }} {% trans "oldin" %}</div>
    # home.html: <div class="tweet-username">@{{ post.author.username }} &middot; {{ post.created_time|timesince }}</div>
    # profile.html: <span style="color: var(--text-muted); font-size: 13px;">@{{ post.author.username }} &middot; {{ post.created_time|date:"d M Y" }}</span>

    # For network.html and home.html
    content = re.sub(
        r'(\{\{\s*post\.created_time\|timesince\s*\}\}\s*(?:\{%\s*trans\s*"oldin"\s*%\}|oldin)?(?!\s*&middot;\s*<span[^>]*fa-star))',
        r'\1' + rating_html,
        content
    )
    
    # For profile.html
    content = re.sub(
        r'(\{\{\s*post\.created_time\|date:"d M Y"\s*\}\}(?!\s*&middot;\s*<span[^>]*fa-star))',
        r'\1' + rating_html,
        content
    )

    with open(file_path, 'w') as f:
        f.write(content)
    print(f"Updated {file_path}")
