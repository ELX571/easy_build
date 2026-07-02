import os
import re

directories = ['templates/build', 'templates/chat', 'templates']
files_to_check = []
for d in directories:
    for root, dirs, files in os.walk(d):
        for file in files:
            if file.endswith('.html'):
                files_to_check.append(os.path.join(root, file))

# Normalize paths and remove duplicates
files_to_check = list(set([os.path.abspath(f) for f in files_to_check]))

meta_tags = """    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0, viewport-fit=cover">
    <meta name="theme-color" content="#05070c" media="(prefers-color-scheme: dark)">
    <meta name="theme-color" content="#f4f6fa" media="(prefers-color-scheme: light)">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="mobile-web-app-capable" content="yes">"""

mobile_css = """
        /* Anti-bounce and App-like scrolling */
        html, body { overscroll-behavior-x: none; overscroll-behavior-y: none; }
        .main-content { overscroll-behavior-y: auto; -webkit-overflow-scrolling: touch; }
        
        /* Hide bottom nav when virtual keyboard is open */
        @media (max-height: 450px) {
            .bottom-nav { display: none !important; }
            body { padding-bottom: 0 !important; }
        }
"""

js_keyboard = """
    <script>
        // PWA App-like Virtual Keyboard handling
        document.addEventListener('DOMContentLoaded', () => {
            const inputs = document.querySelectorAll('input, textarea');
            inputs.forEach(input => {
                input.addEventListener('focus', () => document.body.classList.add('keyboard-open'));
                input.addEventListener('blur', () => document.body.classList.remove('keyboard-open'));
            });
        });
    </script>
"""

for filepath in files_to_check:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated = False
        
        # 1. Update Viewport and Meta tags
        if '<meta name="apple-mobile-web-app-capable"' not in content:
            # Replace existing viewport or insert before <title>
            content = re.sub(r'<meta name="viewport"[^>]+>', meta_tags, content, count=1)
            updated = True
            
        # 2. Add Mobile CSS if bottom-nav exists and css not added
        if 'overscroll-behavior-x: none' not in content:
            # Find the closing style tag and insert before it
            if '</style>' in content:
                content = content.replace('</style>', mobile_css + '\n    </style>')
                updated = True
                
        # 3. Add JS for keyboard if not present
        if 'keyboard-open' not in content and '</body>' in content:
            content = content.replace('</body>', js_keyboard + '\n</body>')
            updated = True
            
        if updated:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

print("Done.")
