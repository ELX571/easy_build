import glob
import re

for f in ['templates/build/home.html', 'templates/build/network.html', 'templates/build/builder_list.html', 'templates/build/dashboard.html']:
    with open(f, 'r') as file:
        content = file.read()
    
    # Remove the strict target user check, allow the buttons to show up!
    # Original: if (d.raw_role === "builder" || d.raw_role === "team" || String(d.role).toLowerCase().includes("usta")) {
    # We will replace it with if (true) {
    
    content = content.replace(
        'if (d.raw_role === "builder" || d.raw_role === "team" || String(d.role).toLowerCase().includes("usta")) {',
        'if (true) {'
    )
    
    # Wait, what if they also want to change isClient?
    # Actually, isClient = "{{ request.user.profile.role }}" === "client";
    # I will change it to not be visible to builders:
    # let isBuilderViewer = "{{ request.user.profile.role }}" === "builder";
    # if (!isBuilderViewer) { ... qiziqish bildirish ... }
    
    content = content.replace(
        'let isClient = "{{ request.user.profile.role }}" === "client";',
        'let isBuilderViewer = "{{ request.user.profile.role }}" === "builder" || "{{ request.user.profile.role }}" === "team";'
    )
    
    content = content.replace(
        'if (isClient) {',
        'if (!isBuilderViewer) {'
    )
    
    with open(f, 'w') as file:
        file.write(content)
    print(f"Updated {f}")

