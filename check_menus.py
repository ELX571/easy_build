import glob

html_files = glob.glob('/home/ismoilow/Desktop/easy_build/templates/**/*.html', recursive=True)

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '<div class="icon-rail">' in content:
        # count number of items in icon-rail
        rail_start = content.find('<div class="icon-rail">')
        rail_end = content.find('</div>', rail_start)
        
        # let's just count fa-solid/fa-regular inside icon-rail to estimate
        rail_content = content[rail_start:content.find('<div class="expanded-menu">', rail_start) if '<div class="expanded-menu">' in content else content.find('</div>\n    </div>', rail_start)]
        
        icons = rail_content.count('fa-house') + rail_content.count('fa-users') + rail_content.count('fa-store') + rail_content.count('fa-helmet-safety') + rail_content.count('fa-comment-dots') + rail_content.count('fa-gem') + rail_content.count('fa-bell') + rail_content.count('fa-user')
        print(f"{file}: {icons} icons in rail")

