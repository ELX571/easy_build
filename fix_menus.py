import glob
import re

html_files = glob.glob('/home/ismoilow/Desktop/easy_build/templates/**/*.html', recursive=True)

# The correct, full icon-rail HTML
correct_rail = """<div class="icon-rail">
            <a href="{% url 'build:home' %}" class="rail-item {% if request.resolver_match.url_name == 'home' %}active{% endif %}" data-title="{% trans 'Bosh sahifa' %}"><i class="fa-solid fa-house"></i></a>
            <a href="{% url 'build:network' %}" class="rail-item {% if request.resolver_match.url_name == 'network' %}active{% endif %}" data-title="{% trans 'Hamkasblar' %}"><i class="fa-solid fa-users"></i></a>
            <a href="{% url 'build:market' %}" class="rail-item {% if request.resolver_match.url_name == 'market' %}active{% endif %}" data-title="Market Pro"><i class="fa-solid fa-store"></i></a>
            <a href="{% url 'build:builder_list' %}" class="rail-item {% if request.resolver_match.url_name == 'builder_list' %}active{% endif %}" data-title="{% trans 'Usta Qidirish' %}"><i class="fa-solid fa-helmet-safety"></i></a>
            <a href="{% url 'chat:chat' %}" class="rail-item {% if request.resolver_match.namespace == 'chat' %}active{% endif %}" data-title="{% trans 'Chatlar' %}">
                <i class="fa-regular fa-comment-dots"></i>
                {% if unread_chat_count > 0 %}
                <span style="position:absolute; top:8px; right:8px; background:var(--active-text-blue); color:white; font-size:10px; font-weight:800; border-radius:50%; width:18px; height:18px; display:flex; align-items:center; justify-content:center;">{{ unread_chat_count }}</span>
                {% endif %}
            </a>
            <a href="{% url 'build:payment_dashboard' %}" class="rail-item {% if request.resolver_match.url_name == 'payment_dashboard' %}active{% endif %}" data-title="Premium"><i class="fa-solid fa-gem"></i></a>
            <a href="{% url 'build:notifications_list' %}" class="rail-item {% if request.resolver_match.url_name == 'notifications_list' %}active{% endif %}" data-title="Bildirishnomalar">
                <i class="fa-solid fa-bell"></i>
                {% if unread_notifications_count > 0 %}
                    <span style="position:absolute; top:8px; right:8px; background:#ef4444; color:white; font-size:10px; font-weight:800; border-radius:50%; width:16px; height:16px; display:flex; align-items:center; justify-content:center; border:2px solid var(--bg-panel);">{{ unread_notifications_count }}</span>
                {% endif %}
            </a>
            <div class="rail-divider"></div>
            <a href="{% url 'build:profile' %}" class="rail-item">
                {% if request.user.profile.avatar %}
                    <img src="{{ request.user.profile.get_avatar_url }}" style="width:100%; height:100%; border-radius:14px; object-fit:cover;">
                {% else %}
                    <i class="fa-regular fa-user"></i>
                {% endif %}
            </a>
        </div>"""

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '<div class="icon-rail">' in content:
        # We need to find where <div class="icon-rail"> starts
        # and where the next </div> that closes it ends.
        # Since the structure is quite simple (no nested divs inside icon-rail usually),
        # we can just use regex with re.DOTALL, but wait, there is <div class="rail-divider"></div> inside.
        # Let's write a simple parser to find the matching closing tag.
        
        start_idx = content.find('<div class="icon-rail">')
        if start_idx != -1:
            div_count = 0
            end_idx = -1
            
            # Simple manual HTML tag balance counting to find the closing div of icon-rail
            # But simpler: we know icon-rail ends right before <div class="expanded-menu">
            # OR if expanded-menu doesn't exist, it ends before </div>\n    </div> (the sidebar-container end)
            
            expanded_idx = content.find('<div class="expanded-menu">', start_idx)
            
            if expanded_idx != -1:
                # the </div> before expanded-menu is our target
                end_idx = content.rfind('</div>', start_idx, expanded_idx) + 6
            else:
                # Find the next </div> that matches the icon-rail
                # Let's just find the closing </div> of sidebar-container and step back
                sidebar_end = content.find('</div>', start_idx + 24)
                # It's better to find the end of rail by searching for the last rail-item's closing tag
                # which is usually </a>
                # then skipping spaces to </div>
                
            # Actually, regex might be easier if we know it ends with </div> and we can be greedy up to the expanded-menu
            # Let's just use the fact that all of them have <div class="sidebar-container">
            # We will use re.sub for the exact rail content.
            # But the content varies.
            pass
            
