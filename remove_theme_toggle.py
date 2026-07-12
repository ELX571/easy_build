import os
import glob

html_files = glob.glob('/home/ismoilow/Desktop/easy_build/templates/**/*.html', recursive=True)

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    changed = False
    new_lines = []
    for line in lines:
        # Remove the HTML button
        if 'id="themeToggleBtn"' in line and '<div' in line:
            changed = True
            continue
        
        # Prevent JS errors
        if "themeToggleBtn.addEventListener" in line and "if" not in line and "if (" not in line:
            line = line.replace("themeToggleBtn.addEventListener", "if(themeToggleBtn) themeToggleBtn.addEventListener")
            changed = True
            
        new_lines.append(line)
        
    if changed:
        with open(file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Updated {file}")

