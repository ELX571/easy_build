import glob
import re

html_files = glob.glob('/home/ismoilow/Desktop/easy_build/templates/**/*.html', recursive=True)

correct_rail = """<div class="icon-rail">
            <a href="{% url 'build:home' %}" class="rail-item {% if request.resolver_match.url_name == 'home' %}active{% endif %}" data-title="Bosh sahifa"><i class="fa-solid fa-house"></i></a>
            <a href="{% url 'build:network' %}" class="rail-item {% if request.resolver_match.url_name == 'network' %}active{% endif %}" data-title="Hamkasblar"><i class="fa-solid fa-users"></i></a>
            <a href="{% url 'build:market' %}" class="rail-item {% if request.resolver_match.url_name == 'market' %}active{% endif %}" data-title="Market Pro"><i class="fa-solid fa-store"></i></a>
            <a href="{% url 'build:builder_list' %}" class="rail-item {% if request.resolver_match.url_name == 'builder_list' %}active{% endif %}" data-title="Usta Qidirish"><i class="fa-solid fa-helmet-safety"></i></a>
            <a href="{% url 'chat:chat' %}" class="rail-item {% if request.resolver_match.namespace == 'chat' %}active{% endif %}" data-title="Chatlar">
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
        # Regex to match <div class="icon-rail"> up to the matching </div> before expanded-menu or another tag
        # Because regex parsing HTML is tricky, let's use a simple algorithm
        parts = content.split('<div class="icon-rail">')
        if len(parts) > 1:
            for i in range(1, len(parts)):
                end_idx = parts[i].find('<div class="expanded-menu">')
                if end_idx == -1:
                    # If expanded-menu is not there, look for the closing of sidebar-container
                    end_idx = parts[i].find('</div>\n    </div>')
                    if end_idx == -1:
                        end_idx = parts[i].find('</div>\n</div>')
                        if end_idx == -1:
                            end_idx = parts[i].find('</div>\n\n')
                
                # We need to find the specific </div> that closes icon-rail
                # It is the </div> right before the expanded_idx
                if end_idx != -1:
                    closing_div_idx = parts[i].rfind('</div>', 0, end_idx)
                    if closing_div_idx != -1:
                        parts[i] = parts[i][closing_div_idx + 6:]
            
            new_content = parts[0]
            for i in range(1, len(parts)):
                new_content += correct_rail + parts[i]
                
            if new_content != content:
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {file}")

