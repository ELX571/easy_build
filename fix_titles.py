import os
import glob
import re

html_files = glob.glob('/home/ismoilow/Desktop/easy_build/templates/**/*.html', recursive=True)

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Use regex to find and replace <title>...</title> safely
    new_content = re.sub(r'<title>.*?</title>', '<title>Easy Build</title>', content, flags=re.DOTALL)
    
    if new_content != content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {file}")

