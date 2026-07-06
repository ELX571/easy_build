import glob
import re

for file_path in glob.glob('templates/**/*.html', recursive=True):
    with open(file_path, 'r') as f:
        content = f.read()

    changed = False

    new_content = re.sub(
        r'<a href="javascript:void\(0\)" onclick="showMarketToast\(\)" data-old="" class="rail-item([^"]*)"[^>]*>(.*?)</a>',
        r'<a href="{% url \'build:market\' %}" class="rail-item {% if request.resolver_match.url_name == \'market\' %}active{% endif %}" data-title="Market Pro">\2</a>',
        content
    )
    
    new_content = re.sub(
        r'<li><a href="javascript:void\(0\)" onclick="showMarketToast\(\)" data-old=""><i class="fa-solid fa-store main-icon"></i> (.*?)</a></li>',
        r'<li><a href="{% url \'build:market\' %}" class="{% if request.resolver_match.url_name == \'market\' %}active-link{% endif %}"><i class="fa-solid fa-store main-icon"></i> \1</a></li>',
        new_content
    )

    if new_content != content:
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"Updated links in {file_path}")
