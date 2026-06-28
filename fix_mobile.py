import os
import glob

# Files to patch for bottom-nav
files = glob.glob('templates/build/*.html') + ['templates/chat/chat.html']

for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    # 1. Update the bottom-nav CSS
    if '.bottom-nav {' in content:
        import re
        # Find the block starting from .bottom-nav { to .badge { ... }
        pattern = re.compile(r'\.bottom-nav \{.*?(?=\@media)', re.DOTALL)
        
        if 'templates/chat/' in f:
            new_nav = """/* ── BOTTOM NAVIGATION (MOBILE) ── */
.bottom-nav { display: none; position: fixed; bottom: calc(15px + env(safe-area-inset-bottom)); left: 15px; width: calc(100% - 30px); height: 65px; background: rgba(13,17,23,0.85); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border: 1px solid var(--border); border-radius: 22px; z-index: 10000; justify-content: space-around; align-items: center; padding: 0 10px; box-shadow: 0 15px 40px rgba(0,0,0,0.5); }
.bottom-nav-item { color: var(--muted); font-size: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 50px; height: 50px; border-radius: 16px; text-decoration: none; position: relative; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.bottom-nav-item.active { color: var(--orange); }
.bottom-nav-item:hover { color: var(--text); background: rgba(255,255,255,0.05); transform: scale(1.1); }
.bottom-nav-item.add-btn { background: linear-gradient(135deg, #ff6b00, #ff8c33); color: #fff !important; border-radius: 50%; width: 54px; height: 54px; transform: translateY(-15px); box-shadow: 0 10px 25px var(--ora); border: 4px solid var(--bg); font-size: 22px; }
.bottom-nav-item.add-btn:hover { transform: translateY(-20px) scale(1.05); box-shadow: 0 14px 30px var(--ora); }
.bottom-nav-item .badge { position: absolute; top: 4px; right: 4px; background: #ef4444; color: #fff; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 10px; border: 2px solid var(--sb); box-shadow: 0 2px 8px rgba(239,68,68,0.4); }

"""
        else:
            new_nav = """/* ── BOTTOM NAVIGATION (MOBILE) ── */
        .bottom-nav { display: none; position: fixed; bottom: calc(15px + env(safe-area-inset-bottom)); left: 15px; width: calc(100% - 30px); height: 65px; background: var(--bg-panel); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border: 1px solid var(--border-color); border-radius: 22px; z-index: 1000; justify-content: space-around; align-items: center; padding: 0 10px; box-shadow: 0 15px 40px rgba(0,0,0,0.25); }
        .bottom-nav-item { color: var(--rail-item-color); font-size: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 50px; height: 50px; border-radius: 16px; text-decoration: none; position: relative; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
        .bottom-nav-item.active { color: var(--active-text-blue); }
        .bottom-nav-item:hover { color: var(--text-main); background: var(--rail-item-hover-bg); transform: scale(1.1); }
        .bottom-nav-item.add-btn { background: linear-gradient(135deg, #ff6b00, #ff8c33); color: #fff !important; border-radius: 50%; width: 54px; height: 54px; transform: translateY(-15px); box-shadow: 0 10px 25px var(--glow-color); border: 4px solid var(--bg-body); font-size: 22px; }
        .bottom-nav-item.add-btn:hover { transform: translateY(-20px) scale(1.05); box-shadow: 0 14px 30px var(--glow-color); }
        .bottom-nav-item .badge { position: absolute; top: 4px; right: 4px; background: #ef4444; color: #fff; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 10px; border: 2px solid var(--bg-panel); box-shadow: 0 2px 8px rgba(239,68,68,0.4); }

        """
        
        content = pattern.sub(new_nav, content)
        
        # 2. Adjust padding in body or main-content
        content = content.replace("padding: 85px 14px 100px 14px;", "padding: 85px 0 120px 0; overflow-x: hidden;")
        content = content.replace("padding: 85px 14px 100px 14px", "padding: 85px 0 120px 0; overflow-x: hidden;")
        
        # for chat.html
        if 'chat.html' in f:
            content = content.replace("height: calc(100vh - 75px);", "height: calc(100vh - 100px);")
            
        with open(f, 'w') as file:
            file.write(content)
        print(f"Updated {f}")

