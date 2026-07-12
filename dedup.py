import os

files_to_check = [
    '/home/ismoilow/Desktop/easy_build/templates/build/network.html',
    '/home/ismoilow/Desktop/easy_build/templates/build/builder_list.html',
    '/home/ismoilow/Desktop/easy_build/templates/base.html'
]

blocks_to_remove = [
    ".custom-dropdown-menu { display: none; position: absolute;",
    ".secure-modal-overlay { position: fixed; inset: 0;",
    "/* MUKAMMAL MOBIL UI UCHUN QO'SHIMCHA SOZLAMALAR */",
    "/* iOS da inputlarga bosganda ekran zoom bo'lib ketmasligi uchun */",
]

for filepath in files_to_check:
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    in_duplicate_block = False
    block_type = None
    
    seen_blocks = set()

    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detect start of custom-dropdown-menu
        if ".custom-dropdown-menu { display: none;" in line:
            if "dropdown" in seen_blocks:
                # skip lines until we see .custom-dropdown-menu .divider
                while i < len(lines) and ".custom-dropdown-menu .divider" not in lines[i]:
                    i += 1
                i += 1 # skip the divider line
                continue
            else:
                seen_blocks.add("dropdown")
                new_lines.append(line)
                i += 1
                continue
                
        # Detect start of secure-modal-overlay
        if ".secure-modal-overlay { position: fixed;" in line:
            if "secure" in seen_blocks:
                while i < len(lines) and ".secure-btn.confirm.active" not in lines[i]:
                    i += 1
                i += 1
                continue
            else:
                seen_blocks.add("secure")
                new_lines.append(line)
                i += 1
                continue

        # Detect start of MUKAMMAL
        if "/* MUKAMMAL MOBIL UI UCHUN" in line:
            if "mukammal" in seen_blocks:
                while i < len(lines):
                    if "@media (max-width: 768px)" in lines[i]:
                        # count braces
                        brace_count = 0
                        while i < len(lines):
                            brace_count += lines[i].count('{')
                            brace_count -= lines[i].count('}')
                            i += 1
                            if brace_count == 0:
                                break
                        break
                    i += 1
                continue
            else:
                seen_blocks.add("mukammal")
                new_lines.append(line)
                i += 1
                continue

        # Check for duplicate toastNotif
        if "id=\"toastNotif\"" in line:
            if "toast" in seen_blocks:
                while i < len(lines) and "</div>" not in lines[i]:
                    i+=1
                i+=1
                # Also skip the style for toast
                while i < len(lines) and ("<style>" in lines[i] or "@keyframes toastPop" in lines[i]):
                    if "</style>" in lines[i]:
                        i+=1
                        break
                    i+=1
                continue
            else:
                seen_blocks.add("toast")
                new_lines.append(line)
                i+=1
                continue

        # Check for duplicate contactModal
        if "id=\"contactModal\"" in line:
            if "contactModal" in seen_blocks:
                div_count = 0
                while i < len(lines):
                    div_count += lines[i].count('<div')
                    div_count -= lines[i].count('</div')
                    i += 1
                    if div_count <= 0:
                        break
                continue
            else:
                seen_blocks.add("contactModal")
                new_lines.append(line)
                i += 1
                continue

        new_lines.append(line)
        i += 1
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"Cleaned logic {filepath}")

