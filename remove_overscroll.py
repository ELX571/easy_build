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
        
        # Remove overscroll rules
        if 'overscroll-behavior-x: none' in content:
            content = re.sub(r'\s*/\*\s*Anti-bounce and App-like scrolling\s*\*/\s*html, body \{ overscroll-behavior-x: none; overscroll-behavior-y: none; \}\s*\.main-content \{ overscroll-behavior-y: auto; -webkit-overflow-scrolling: touch; \}', '', content)
            
            # also fallback if regex misses due to spaces
            content = content.replace('html, body { overscroll-behavior-x: none; overscroll-behavior-y: none; }', '')
            content = content.replace('.main-content { overscroll-behavior-y: auto; -webkit-overflow-scrolling: touch; }', '')
            content = content.replace('/* Anti-bounce and App-like scrolling */', '')
            
            updated = True
            
        if updated:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

print("Done.")
