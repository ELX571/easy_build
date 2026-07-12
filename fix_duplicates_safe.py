import re

files_to_check = [
    '/home/ismoilow/Desktop/easy_build/templates/build/network.html',
    '/home/ismoilow/Desktop/easy_build/templates/build/builder_list.html',
    '/home/ismoilow/Desktop/easy_build/templates/base.html'
]

def clean_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = []
    
    # Block 1
    b1 = """        .custom-dropdown-menu { display: none; position: absolute; right: 0; top: 40px; background: var(--bg-panel); border: 1px solid var(--border-color); border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); min-width: 200px; z-index: 100; overflow: hidden; flex-direction: column; }
        .custom-dropdown-menu.show { display: flex; }
        .custom-dropdown-menu a { padding: 12px 16px; color: var(--text-main); text-decoration: none; font-size: 15px; display: flex; align-items: center; gap: 10px; transition: background 0.2s; }
        .custom-dropdown-menu a:hover { background: var(--link-hover-bg); }
        .custom-dropdown-menu .text-danger { color: #ef4444 !important; }
        .custom-dropdown-menu .text-warning { color: #f59e0b !important; }
        .custom-dropdown-menu .divider { height: 1px; background: var(--border-color); margin: 4px 0; }"""
    blocks.append(b1)
    
    # Block 2
    b2 = """        .secure-modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(10px); z-index: 9999; display: none; align-items: center; justify-content: center; padding: 20px; }
        .secure-modal { background: #ffffff; color: #0f172a; width: 100%; max-width: 440px; border-radius: 24px; padding: 28px; box-shadow: 0 25px 50px rgba(0,0,0,0.3); display: flex; flex-direction: column; gap: 16px; border: 1px solid #cbd5e1; }
        .secure-title { font-size: 18px; font-weight: 800; color: #ef4444; display: flex; align-items: center; gap: 8px; }
        .secure-desc { font-size: 14px; color: #475569; line-height: 1.5; font-weight: 500; }
        .secure-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 4px; }
        .secure-btn { padding: 12px; border-radius: 12px; font-size: 14px; font-weight: 700; cursor: pointer; border: none; text-align: center; text-decoration: none; }
        .secure-btn.cancel { background: #f1f5f9; color: #475569; }
        .secure-btn.confirm { background: #cbd5e1; color: #94a3b8; cursor: not-allowed; transition: all 0.3s ease; }
        .secure-btn.confirm.active { background: #ef4444; color: #ffffff; cursor: pointer; box-shadow: 0 4px 14px rgba(239,68,68,0.4); }"""
    blocks.append(b2)
    
    # Block 3
    b3 = """        /* MUKAMMAL MOBIL UI UCHUN QO'SHIMCHA SOZLAMALAR */
        html { overflow-x: hidden !important; width: 100vw !important; max-width: 100% !important; }
        body {
            overflow-x: hidden !important;
            width: 100% !important; 
            max-width: 100vw !important;
            position: relative;
            -webkit-tap-highlight-color: transparent;
        }
        
        .logo { white-space: nowrap !important; display: block !important; line-height: 1 !important; display: flex !important; align-items: center !important; }

        @media (max-width: 768px) {
            /* iOS da inputlarga bosganda ekran zoom bo'lib ketmasligi uchun */
            input, textarea, select { font-size: 16px !important; }
            
            /* Tepa panel moslashuvi (Notch kirmasligi uchun) */
            header {
                padding-top: env(safe-area-inset-top, 0px) !important;
                padding-left: 14px !important;
                padding-right: 14px !important;
                height: calc(64px + env(safe-area-inset-top, 0px)) !important;
            }
            .header-add-btn { width: 40px !important; height: 40px !important; }

            /* Asosiy kontent moslashuvi */
            .main-content {
                padding-top: calc(85px + env(safe-area-inset-top, 0px)) !important;
                padding-bottom: calc(100px + env(safe-area-inset-bottom, 0px)) !important;
                padding-left: 0 !important; padding-right: 0 !important;
                width: 100% !important;
            }
            
            /* Grid va qidiruv bo'limlari chetidan joy qoldirish */
            .market-filter-bar, .builders-grid-layout, .profile-container, .form-container, .auth-wrapper {
                padding-left: 14px !important;
                padding-right: 14px !important;
            }

            /* Edge-to-Edge tweet cards */
            .twitter-feed { gap: 10px !important; margin-bottom: 30px !important; }
            .tweet-card {
                border-radius: 0 !important;
                border-left: none !important;
                border-right: none !important;
                margin-left: 0 !important; margin-right: 0 !important;
                border-top: 1px solid var(--border-color) !important;
                border-bottom: 1px solid var(--border-color) !important;
            }
            
            /* Bottom Nav (Pastki menyu moslashuvi) */
            .bottom-nav {
                display: flex !important;
                padding-bottom: env(safe-area-inset-bottom, 0px) !important;
                height: calc(65px + env(safe-area-inset-bottom, 0px)) !important;
                bottom: 0 !important; width: 100% !important; left: 0 !important;
                border-radius: 0 !important; border-left: none !important; border-right: none !important; border-bottom: none !important;
            }
            
            /* Modallar va Bottom sheets */
            .secure-modal-overlay { align-items: flex-end !important; padding: 0 !important; }
            .secure-modal, #contactModalInner {
                margin: 0 !important; max-width: 100% !important;
                border-radius: 32px 32px 0 0 !important; border-bottom: none !important;
            }
        }"""
    blocks.append(b3)

    for block in blocks:
        parts = content.split(block)
        if len(parts) > 2:
            # Rejoin the first two with block (keeping one), and the rest without block (removing others)
            content = parts[0] + block + "".join(parts[1:])
            
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
for f in files_to_check:
    clean_file(f)
