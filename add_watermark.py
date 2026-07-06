import glob
import re

for file_path in glob.glob('templates/**/*.html', recursive=True):
    with open(file_path, 'r') as f:
        content = f.read()

    changed = False

    # Check and add --watermark variables in :root
    if ':root {' in content and '--watermark-color' not in content:
        content = re.sub(
            r'(:root\s*\{)',
            r'\1\n            --watermark-color: var(--active-text-blue);\n            --watermark-opacity: 0.08;',
            content
        )
        changed = True

    # Check and add --watermark variables in [data-theme="dark"]
    if '[data-theme="dark"] {' in content and '--watermark-opacity: 0.05' not in content and '--watermark-opacity: 0.03' not in content:
        content = re.sub(
            r'(\[data-theme="dark"\]\s*\{)',
            r'\1\n            --watermark-color: var(--active-text-blue);\n            --watermark-opacity: 0.03;',
            content
        )
        changed = True
        
    # Check if .bg-watermark class is present
    if '.bg-watermark' not in content and '<style>' in content:
        content = content.replace(
            '<style>',
            '<style>\n        .bg-watermark { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 70vh; color: var(--watermark-color); opacity: var(--watermark-opacity); z-index: -2; pointer-events: none; transition: all 0.4s ease; }'
        )
        changed = True
        
    # Check if the HTML element is present
    if 'bg-watermark' not in content or '<i class="fa-solid fa-helmet-safety bg-watermark"></i>' not in content:
        # Avoid double adding if class name is present but different tag (though we only have fa-helmet-safety)
        if '<i class="fa-solid fa-helmet-safety bg-watermark"></i>' not in content:
            content = content.replace(
                '<body>',
                '<body>\n    <i class="fa-solid fa-helmet-safety bg-watermark"></i>'
            )
            changed = True

    if changed:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Added watermark to {file_path}")
