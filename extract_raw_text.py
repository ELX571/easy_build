import os
import re

html_dir = 'templates'
raw_texts = set()

# A rough regex to find text outside of Django tags
def extract_text(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Remove script and style tags
    content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL)
    
    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    # Find text between > and <
    matches = re.findall(r'>([^<]+)<', content)
    
    for match in matches:
        match = match.strip()
        if not match:
            continue
        # Skip if it's already translated or contains a variable
        if '{% trans' in match or '{%' in match or '{{' in match:
            continue
        # Skip if it's just punctuation, numbers, or symbols
        if re.match(r'^[\W\d_]+$', match):
            continue
        # Skip font-awesome icons, etc.
        if match in ['uz', 'ru', 'en']:
            continue
            
        raw_texts.add((match, filepath))

for root, _, files in os.walk(html_dir):
    for f in files:
        if f.endswith('.html'):
            extract_text(os.path.join(root, f))

with open('raw_texts.txt', 'w') as f:
    for text, path in sorted(list(raw_texts)):
        f.write(f"[{path}] {text}\n")

print("Done. Found", len(raw_texts), "raw strings.")
