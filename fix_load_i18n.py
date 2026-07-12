import os
import re

files_to_fix = [
    "templates/build/post_list.html",
    "templates/build/profile.html",
    "templates/build/home.html",
    "templates/build/workflow_list.html",
    "templates/build/plans.html",
    "templates/build/payment_dashboard.html",
    "templates/build/notifications.html",
    "templates/build/verification.html",
    "templates/build/marketb2bpro.html",
    "templates/base.html",
    "templates/accounts/step1_register.html",
    "templates/accounts/second_register.html",
    "templates/accounts/login.html",
    "templates/accounts/register.html"
]

for file in files_to_fix:
    if not os.path.exists(file): continue
    with open(file, 'r') as f:
        content = f.read()
        
    if '{% load i18n %}' in content:
        continue
        
    # Check if there is an extends tag
    extends_match = re.search(r'{% extends [^}]+ %}\n?', content)
    if extends_match:
        # insert after extends
        end = extends_match.end()
        new_content = content[:end] + '{% load i18n %}\n' + content[end:]
    else:
        # Check if there is load static
        load_static_match = re.search(r'{% load static %}\n?', content)
        if load_static_match:
            end = load_static_match.end()
            new_content = content[:end] + '{% load i18n %}\n' + content[end:]
        else:
            new_content = '{% load i18n %}\n' + content
            
    with open(file, 'w') as f:
        f.write(new_content)
        print(f"Fixed {file}")

print("Done")
