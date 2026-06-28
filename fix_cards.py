import glob

# For home, post_list, profile
files = glob.glob('templates/build/*.html')

for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    if '.tweet-card {' in content and '@media (max-width: 768px)' in content:
        # We need to inject styles into the @media (max-width: 768px)
        if '.tweet-card { padding: 18px 16px; border-radius: 20px; gap: 14px; }' in content:
            content = content.replace('.tweet-card { padding: 18px 16px; border-radius: 20px; gap: 14px; }', 
            '.tweet-card { padding: 18px 0; border-radius: 0; border-left: none; border-right: none; margin: 0 -14px; gap: 12px; box-shadow: none; border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); background: var(--bg-body); }\n'
            '            .tweet-header, .tweet-body, .tweet-price-badge, .tweet-manage-toolbar, .tweet-footer, .tweet-stats, .tweet-manage-actions { padding-left: 16px; padding-right: 16px; }\n'
            '            .tweet-image { width: 100%; border-radius: 0; border-left: none; border-right: none; margin-top: 8px; margin-bottom: 8px; max-height: 400px; }')
        
        # Profile might have slightly different tweet card styles or missing mobile tweet-card patch
        if 'profile.html' in f:
            if '.tweet-card {' not in content.split('@media (max-width: 768px)')[1]:
                # inject it
                injection = """
            .tweet-card { padding: 18px 0; border-radius: 0; border-left: none; border-right: none; margin: 0 -14px; gap: 12px; box-shadow: none; border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); background: var(--bg-body); }
            .tweet-header, .tweet-body, .tweet-price-badge, .tweet-manage-toolbar, .tweet-footer, .tweet-stats, .tweet-manage-actions { padding-left: 16px; padding-right: 16px; }
            .tweet-image { width: 100%; border-radius: 0; border-left: none; border-right: none; margin-top: 8px; margin-bottom: 8px; max-height: 400px; }
            .profile-header-card { margin: 0 -14px; border-radius: 0; border-left: none; border-right: none; border-top: none; }
            """
                content = content.replace('body { padding: 85px 0 120px 0; overflow-x: hidden; }', 'body { padding: 85px 0 120px 0; overflow-x: hidden; }' + injection)

        with open(f, 'w') as file:
            file.write(content)
        print(f"Updated cards in {f}")

