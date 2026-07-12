import re
import os

files_to_check = [
    '/home/ismoilow/Desktop/easy_build/templates/build/network.html',
    '/home/ismoilow/Desktop/easy_build/templates/build/builder_list.html',
    '/home/ismoilow/Desktop/easy_build/templates/base.html'
]

pattern_dropdown = re.compile(r'\s*\.custom-dropdown-menu\s*\{.*?\}\s*\.custom-dropdown-menu\.show.*?\}\s*\.custom-dropdown-menu a\s*\{.*?\}\s*\.custom-dropdown-menu a:hover.*?\}\s*\.custom-dropdown-menu \.text-danger.*?\}\s*\.custom-dropdown-menu \.text-warning.*?\}\s*\.custom-dropdown-menu \.divider.*?\}', re.DOTALL)

pattern_secure = re.compile(r'\s*\.secure-modal-overlay\s*\{.*?\}\s*\.secure-modal\s*\{.*?\}\s*\.secure-title\s*\{.*?\}\s*\.secure-desc\s*\{.*?\}\s*\.secure-actions\s*\{.*?\}\s*\.secure-btn\s*\{.*?\}\s*\.secure-btn\.cancel\s*\{.*?\}\s*\.secure-btn\.confirm\s*\{.*?\}\s*\.secure-btn\.confirm\.active\s*\{.*?\}', re.DOTALL)

pattern_mobile = re.compile(r'\s*/\*\s*MUKAMMAL MOBIL UI UCHUN.*?\}\s*\}\s*', re.DOTALL)

for filepath in files_to_check:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove duplicates by keeping only the first match
    
    def remove_duplicates(content, pattern):
        matches = list(pattern.finditer(content))
        if len(matches) > 1:
            for match in reversed(matches[1:]):
                content = content[:match.start()] + content[match.end():]
        return content

    content = remove_duplicates(content, pattern_dropdown)
    content = remove_duplicates(content, pattern_secure)
    content = remove_duplicates(content, pattern_mobile)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Cleaned {filepath}")
