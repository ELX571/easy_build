import re

file_path = 'templates/build/marketb2bpro.html'
with open(file_path, 'r') as f:
    content = f.read()

rating_html = """ <span style="color:#f59e0b; font-weight:600; display:inline-flex; align-items:center; gap:3px; margin-left:6px;"><i class="fa-solid fa-star" style="font-size:11px;"></i> {{ post.author.profile.rating_average|floatformat:1 }}</span>"""

content = re.sub(
    r'(<span class="card-author-name"><i class="fa-regular fa-circle-user"></i>\s*@\{\{\s*post\.author\.username\s*\}\})(?! <span)',
    r'\1' + rating_html,
    content
)

with open(file_path, 'w') as f:
    f.write(content)
print(f"Updated {file_path}")
