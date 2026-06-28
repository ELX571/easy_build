import glob

files = glob.glob('templates/build/*.html')

for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    new_content = content.replace('padding: 85px 0 120px 0;', 'padding: 85px 14px 120px 14px;')
    
    if new_content != content:
        with open(f, 'w') as file:
            file.write(new_content)
        print(f"Fixed padding in {f}")

