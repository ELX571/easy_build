import os
import re
import subprocess
import time
from deep_translator import GoogleTranslator

# 1. Read raw texts and patch HTMLs
print("Patching HTML files...")
html_modifications = {}
with open('raw_texts.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        # [path] text
        match = re.match(r'^\[(.*?)\] (.*)$', line)
        if match:
            path, text = match.groups()
            if path not in html_modifications:
                html_modifications[path] = []
            html_modifications[path].append(text)

for path, texts in html_modifications.items():
    if not os.path.exists(path): continue
    with open(path, 'r') as f:
        content = f.read()
    
    modified = False
    for text in texts:
        # Be careful not to replace inside tags, only text between > <
        # Since it's exactly the text we extracted, >text< should work mostly.
        # But text might have newlines if we are not careful.
        # It's safer to do simple replace since we extracted it strictly.
        target = f">{text}<"
        replacement = f">{{% trans \"{text}\" %}}<"
        if target in content:
            content = content.replace(target, replacement)
            modified = True
            
    if modified:
        with open(path, 'w') as f:
            f.write(content)

print("Running makemessages...")
subprocess.run(['.venv/bin/python', 'manage.py', 'makemessages', '-l', 'ru', '-l', 'en'], check=True)

# 2. Translate empty msgstr in PO files
def translate_po(lang, target_lang_code):
    print(f"Translating PO file for {lang}...")
    po_path = f'locale/{lang}/LC_MESSAGES/django.po'
    if not os.path.exists(po_path):
        return
        
    with open(po_path, 'r') as f:
        content = f.read()
        
    translator = GoogleTranslator(source='uz', target=target_lang_code)
    
    # regex to find msgid "..." followed by msgstr ""
    # Note: this is a simple regex that assumes no multiline msgids for simplicity
    pattern = r'msgid "(.*?)"\nmsgstr ""'
    
    def replacer(match):
        uz_text = match.group(1)
        if not uz_text:
            return match.group(0)
        try:
            translated = translator.translate(uz_text)
            # escape quotes
            translated = translated.replace('"', '\\"')
            time.sleep(0.1) # to prevent rate limiting
            return f'msgid "{uz_text}"\nmsgstr "{translated}"'
        except Exception as e:
            print(f"Failed to translate {uz_text}: {e}")
            return match.group(0)
            
    new_content = re.sub(pattern, replacer, content)
    
    with open(po_path, 'w') as f:
        f.write(new_content)

translate_po('ru', 'ru')
translate_po('en', 'en')

print("Running compilemessages...")
subprocess.run(['.venv/bin/python', 'manage.py', 'compilemessages'], check=True)
subprocess.run(['touch', 'conf/settings.py'], check=True)
print("All Done!")
