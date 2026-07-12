import re

with open('templates/build/profile_edit.html', 'r') as f:
    content = f.read()

# We want to replace the `billing-toggle` and `pricing-cards` and its CSS with the new layout.
# The `setting-verification` block starts at:
#         <div class="settings-content" id="setting-verification" style="display: none;">
#             <div class="verif-title">
#                 <i class="fa-solid fa-wallet"></i> {% trans "Verifikatsiya & Obunalar" %}
#             </div>
#             <style> ... </script>

start_marker = r'<div class="settings-content" id="setting-verification" style="display: none;">\s*<div class="verif-title">\s*<i class="fa-solid fa-wallet"></i> {% trans "Verifikatsiya & Obunalar" %}\s*</div>'

# We find where `{% if profile.role == 'team' %}` is (around line 941).
# We'll regex replace from start_marker to just before that.
# Or better, we can replace the `<style> ... <script>` inside setting-verification.
import ast

def replace_block():
    global content
    
    css = """
    <style>
    .bg-watermark { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 70vh; color: var(--watermark-color); opacity: var(--watermark-opacity); z-index: -2; pointer-events: none; transition: all 0.4s ease; }
    .verif-title {
        font-size: 22px;
        font-weight: 800;
        color: #f8fafc;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 30px;
    }
    .verif-title i { color: #f97316; }
    
    /* New Plan Cards CSS */
    .plan-cards {
        display: grid;
        grid-template-columns: 1fr;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    @media (min-width: 768px) {
        .plan-cards { grid-template-columns: repeat(2, 1fr); }
    }
    
    @media (min-width: 1200px) {
        .plan-cards { grid-template-columns: repeat(4, 1fr); }
    }

    .plan-card {
        cursor: pointer;
        position: relative;
        display: block;
        margin: 0;
        height: 100%;
        text-decoration: none;
    }

    /* Oq rangli standart kartalar */
    .plan-card-content {
        background: #ffffff;
        border: 2px dashed rgba(37, 99, 235, 0.4);
        border-radius: 28px;
        padding: 2.5rem 2rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        height: 100%;
        position: relative;
        color: #1e293b;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        overflow: visible;
    }

    .plan-card:nth-child(2) .plan-card-content {
        border: none;
        box-shadow: 0 15px 40px rgba(0,0,0,0.1);
    }
    
    .plan-card:nth-child(3) .plan-card-content {
        border: 2px solid #2563eb;
        transform: translateY(-10px);
        box-shadow: 0 20px 50px rgba(37, 99, 235, 0.15);
    }

    /* Qora/Maxsus karta */
    .plan-card.maxsus-card .plan-card-content {
        background: #0f172a;
        border: none;
        color: #ffffff;
        box-shadow: 0 20px 50px rgba(0,0,0,0.3);
    }

    .plan-badge {
        position: absolute;
        top: -15px;
        left: 50%;
        transform: translateX(-50%);
        background: #2563eb;
        color: white;
        font-size: 0.75rem;
        font-weight: 800;
        padding: 6px 20px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
        z-index: 2;
        white-space: nowrap;
    }

    .badge-maxsus {
        background: linear-gradient(135deg, #1e293b, #334155);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
    
    .plan-name-top {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
        color: #64748b;
        margin-bottom: 1rem;
        font-style: italic;
    }
    
    .plan-card.maxsus-card .plan-name-top {
        color: #94a3b8;
    }

    .plan-price-large {
        font-size: 3.5rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: baseline;
        gap: 0.5rem;
    }
    
    .plan-card.maxsus-card .plan-price-large {
        color: #ffffff;
        font-size: 2.5rem;
    }

    .plan-price-period {
        font-size: 1rem;
        font-weight: 600;
        color: #64748b;
    }
    
    .plan-card.maxsus-card .plan-price-period {
        color: #94a3b8;
    }

    .plan-desc {
        font-size: 0.85rem;
        font-weight: 700;
        color: #2563eb;
        text-transform: uppercase;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .plan-card.maxsus-card .plan-desc {
        color: #60a5fa;
        border-bottom-color: rgba(255,255,255,0.1);
    }

    .plan-features {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .feature-item {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        font-size: 0.95rem;
        font-weight: 600;
        color: #334155;
    }
    
    .plan-card.maxsus-card .feature-item {
        color: #cbd5e1;
    }

    .feature-icon {
        color: #10b981;
        font-size: 1rem;
        margin-top: 2px;
    }
    
    .feature-icon.blue {
        color: #2563eb;
    }

    .plan-btn {
        width: 100%;
        padding: 1rem;
        border-radius: 12px;
        font-size: 1.05rem;
        font-weight: 700;
        text-align: center;
        transition: all 0.3s ease;
        background: #f1f5f9;
        color: #2563eb;
        border: none;
        cursor: pointer;
    }
    
    .plan-card:nth-child(3) .plan-btn {
        background: #2563eb;
        color: white;
        box-shadow: 0 10px 20px rgba(37, 99, 235, 0.3);
    }
    
    .plan-card.maxsus-card .plan-btn {
        background: white;
        color: #0f172a;
    }
    
    .plan-card:hover .plan-card-content {
        transform: translateY(-5px);
    }
    .plan-card:nth-child(3):hover .plan-card-content {
        transform: translateY(-15px);
    }
    </style>
    
    <div class="plan-cards">
        <!-- 1. Boshlang'ich -->
        <div class="plan-card">
            <div class="plan-card-content">
                <div class="plan-name-top">SINOV MUDDATI</div>
                <div class="plan-price-large">
                    0<span class="plan-price-period">so'm/3 kun</span>
                </div>
                <div class="plan-desc">Tizimni to'liq sinash</div>
                
                <div class="plan-features">
                    <div class="feature-item">
                        <i class="fa-solid fa-check-double feature-icon blue"></i>
                        <span>To'liq funksionallik</span>
                    </div>
                    <div class="feature-item">
                        <i class="fa-solid fa-check feature-icon"></i>
                        <span>3 kunlik kirish ruxsati</span>
                    </div>
                    <div class="feature-item">
                        <i class="fa-solid fa-check feature-icon"></i>
                        <span>Buyurtmalarga taklif berish</span>
                    </div>
                    <div class="feature-item">
                        <i class="fa-solid fa-check feature-icon"></i>
                        <span>Reytingni oshirish</span>
                    </div>
                </div>
                
                <button class="plan-btn" style="background: rgba(255,255,255,0.05); color: #94a3b8; cursor: default; border: 1px dashed #cbd5e1;">✓ Faol</button>
            </div>
        </div>

        <!-- 2. Standard -->
        <div class="plan-card">
            <div class="plan-card-content">
                <div class="plan-name-top">STANDARD</div>
                <div class="plan-price-large">
                    49,000<span class="plan-price-period">so'm/oy</span>
                </div>
                <div class="plan-desc">Barcha asosiy funksiyalar</div>
                
                <div class="plan-features">
                    <div class="feature-item">
                        <i class="fa-solid fa-check-double feature-icon blue"></i>
                        <span>To'liq funksionallik</span>
                    </div>
                    <div class="feature-item">
                        <i class="fa-solid fa-check feature-icon"></i>
                        <span>Ko'k tasdiq belgisi</span>
                    </div>
                    <div class="feature-item">
                        <i class="fa-solid fa-check feature-icon"></i>
                        <span>O'z jamoasini yaratish</span>
                    </div>
                    <div class="feature-item">
                        <i class="fa-solid fa-check feature-icon"></i>
                        <span>Mijozlarga aloqaga chiqish</span>
                    </div>
                </div>
                
                <button type="button" class="plan-btn" onclick="openPayModal('pro')">Tanlash</button>
            </div>
        </div>

        <!-- 3. Pro -->
        <div class="plan-card">
            <div class="plan-card-content">
                <div class="plan-badge">TAVSIYA ETILADI</div>
                <div class="plan-name-top">PRO</div>
                <div class="plan-price-large">
                    99,000<span class="plan-price-period">so'm/oy</span>
                </div>
                <div class="plan-desc">Barcha funksiyalar ochiq</div>
                
                <div class="plan-features">
                    <div class="feature-item">
                        <i class="fa-solid fa-check-double feature-icon blue"></i>
                        <span>To'liq funksionallik</span>
                    </div>
                    <div class="feature-item">
                        <i class="fa-solid fa-building feature-icon blue"></i>
                        <span>Yirik jamoalar uchun maxsus</span>
                    </div>
                    <div class="feature-item">
                        <i class="fa-solid fa-rocket feature-icon" style="color: #f97316;"></i>
                        <span>Top ro'yxatlarda turish</span>
                    </div>
                    <div class="feature-item">
                        <i class="fa-solid fa-headset feature-icon blue"></i>
                        <span>VIP Texnik yordam 24/7</span>
                    </div>
                </div>
                
                <button type="button" class="plan-btn" onclick="openPayModal('pro')">Sotib olish</button>
            </div>
        </div>

        <!-- 4. Maxsus -->
        <div class="plan-card maxsus-card">
            <div class="plan-card-content">
                <div class="plan-name-top">INDIVIDUAL</div>
                <div class="plan-price-large">MAXSUS</div>
                <div class="plan-desc">Shaxsiy kelishuv asosida</div>
                
                <div class="plan-features">
                    <div class="feature-item">
                        <i class="fa-solid fa-check-double feature-icon blue"></i>
                        <span>To'liq funksionallik</span>
                    </div>
                    <div class="feature-item">
                        <i class="fa-solid fa-handshake feature-icon"></i>
                        <span>Shaxsiy kelishuv</span>
                    </div>
                    <div class="feature-item">
                        <i class="fa-solid fa-crown feature-icon" style="color: #fbbf24;"></i>
                        <span>Oltin tasdiq belgisi</span>
                    </div>
                    <div class="feature-item">
                        <i class="fa-solid fa-users feature-icon"></i>
                        <span>Jamoa a'zolari soniga ko'ra</span>
                    </div>
                </div>
                
                <button type="button" class="plan-btn" onclick="openPayModal('vip')">Muzokara qilish</button>
            </div>
        </div>
    </div>
"""

    # We need to find setting-verification content and replace
    start_tag = r'<div class="settings-content" id="setting-verification" style="display: none;">\s*<div class="verif-title">\s*<i class="fa-solid fa-wallet"></i> {% trans "Verifikatsiya & Obunalar" %}\s*</div>'
    match = re.search(start_tag, content)
    if not match:
        print("Start tag not found")
        return
        
    start_idx = match.end()
    
    # find the next `{% if profile.role == 'team' %}` or `</div>` that closes setting-verification.
    # From line 639 to 938 it is `<div class="settings-content" id="setting-verification" style="display: none;">`
    # The end of this div is just before `{% if profile.role == 'team' %}`
    
    end_tag = r'{% if profile.role == \'team\' %}'
    end_match = re.search(end_tag, content[start_idx:])
    
    if not end_match:
        print("End tag not found")
        return
        
    end_idx = start_idx + end_match.start()
    
    # We replace everything between start_idx and the closing </div> of setting-verification which is just before end_idx
    # Let's just find the last </div> before end_tag
    sub_content = content[start_idx:end_idx]
    last_div_idx = sub_content.rfind('</div>')
    
    if last_div_idx != -1:
        new_content = content[:start_idx] + "\n" + css + "\n" + content[start_idx + last_div_idx:]
        with open('templates/build/profile_edit.html', 'w') as f:
            f.write(new_content)
        print("Successfully updated profile_edit.html")
    else:
        print("Could not find closing div")

replace_block()
