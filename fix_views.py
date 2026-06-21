import re

with open('/home/ismoilow/Desktop/easy_build/build/views.py', 'r') as f:
    lines = f.readlines()

new_lines = []
in_class = False
for line in lines:
    if line.startswith('class '):
        in_class = True
        new_lines.append(line)
    elif line.startswith('    def '):
        in_class = True
        new_lines.append(line)
    elif in_class and not line.startswith(' ') and line.strip():
        in_class = False
        new_lines.append(line)
    elif in_class and line.strip():
        # Fix indentation
        # We know the baseline was 4 spaces. We want to make it 8 spaces.
        # But wait, some lines were already modified by my previous script.
        # Let's count current leading spaces:
        leading = len(line) - len(line.lstrip(' '))
        if leading == 4:
            new_lines.append(' ' * 8 + line.lstrip())
        elif leading == 8:
            # Could be a statement that was originally 4 spaces and got fixed to 8,
            # or a statement that was originally 8 spaces and got left at 8.
            # Let's check context.
            pass
        
        # Actually it's easier to just fetch from the original git repo if available.
