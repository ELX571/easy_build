import glob
import re

for file_path in glob.glob('templates/**/*.html', recursive=True):
    with open(file_path, 'r') as f:
        content = f.read()

    new_content = content.replace(r"{% url \'build:market\' %}", "{% url 'build:market' %}")
    new_content = new_content.replace(r"request.resolver_match.url_name == \'market\'", "request.resolver_match.url_name == 'market'")

    if new_content != content:
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"Fixed backslashes in {file_path}")
