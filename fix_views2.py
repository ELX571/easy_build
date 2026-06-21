import re

with open('/home/ismoilow/Desktop/easy_build/build/views.py', 'r') as f:
    lines = f.readlines()

out = []
for i, line in enumerate(lines):
    # Fix the blocks that got shifted
    if line.startswith('        # ============================================================================='):
        out.append(line.replace('        ', '', 1))
    elif line.startswith('        @login_required'):
        out.append(line.replace('        ', '', 1))
    elif line.startswith('        def profile_view('):
        out.append(line.replace('        ', '', 1))
    elif line.startswith('        def profile_edit_view('):
        out.append(line.replace('        ', '', 1))
    elif line.startswith('        @require_POST'):
        out.append(line.replace('        ', '', 1))
    elif line.startswith('        def post_create_view('):
        out.append(line.replace('        ', '', 1))
    elif line.startswith('        def builder_list_view('):
        out.append(line.replace('        ', '', 1))
    else:
        out.append(line)

with open('/home/ismoilow/Desktop/easy_build/build/views.py', 'w') as f:
    f.writelines(out)

