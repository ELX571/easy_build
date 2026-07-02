import os
import re

directories = ['templates/build', 'templates/chat', 'templates/accounts', 'templates']
files_to_check = []
for d in directories:
    if os.path.exists(d):
        for root, dirs, files in os.walk(d):
            for file in files:
                if file.endswith('.html'):
                    files_to_check.append(os.path.join(root, file))

files_to_check = list(set([os.path.abspath(f) for f in files_to_check]))

for filepath in files_to_check:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated = False
        
        # Remove media max-height
        if '@media (max-height: 450px)' in content:
            content = re.sub(r'\s*/\*\s*Hide bottom nav when virtual keyboard is open\s*\*/\s*@media \(max-height: 450px\) \{\s*\.bottom-nav \{ display: none !important; \}\s*body \{ padding-bottom: 0 !important; \}\s*\}', '', content)
            updated = True
            
        # Remove js_keyboard
        if 'keyboard-open' in content:
            content = re.sub(r'\s*<script>\s*// PWA App-like Virtual Keyboard handling\s*document\.addEventListener\(\'DOMContentLoaded\', \(\) => \{\s*const inputs = document\.querySelectorAll\(\'input, textarea\'\);\s*inputs\.forEach\(input => \{\s*input\.addEventListener\(\'focus\', \(\) => document\.body\.classList\.add\(\'keyboard-open\'\)\);\s*input\.addEventListener\(\'blur\', \(\) => document\.body\.classList\.remove\(\'keyboard-open\'\)\);\s*\}\);\s*\}\);\s*</script>', '', content)
            updated = True
            
        # Also let's remove PWA meta tags since they might be causing it to launch standalone for the user
        if '<meta name="apple-mobile-web-app-capable"' in content:
            content = re.sub(r'\s*<meta name="apple-mobile-web-app-capable" content="yes">\s*<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\s*<meta name="mobile-web-app-capable" content="yes">', '', content)
            updated = True
            
        if updated:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

print("Done.")
