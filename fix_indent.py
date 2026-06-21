with open('/home/ismoilow/Desktop/easy_build/build/views.py', 'r') as f:
    lines = f.readlines()

out = []
in_class_method = False
for line in lines:
    if line.startswith('class '):
        in_class_method = False
    elif line.startswith('    def '):
        in_class_method = True
        out.append(line)
        continue
    
    if in_class_method and line.strip() and not line.startswith('        '):
        # Needs indentation
        if line.startswith('    '):
            out.append('    ' + line)
        else:
            out.append('        ' + line)
    else:
        # Check if line is completely empty and in class method
        if in_class_method and not line.strip():
            out.append(line)
        else:
            out.append(line)

with open('/home/ismoilow/Desktop/easy_build/build/views.py', 'w') as f:
    f.writelines(out)

print("Done")
