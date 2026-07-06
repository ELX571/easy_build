import glob

# Javascript code to append to btns
extra_js = """
        // Qiziqish va Kelishish buttonlari
        let isClient = "{{ request.user.profile.role }}" === "client";
        
        if (d.raw_role === "builder" || d.raw_role === "team" || String(d.role).toLowerCase().includes("usta")) {
            btns += `<button onclick="sendNegotiate(${userId})" style="display:flex;align-items:center;gap:14px;padding:16px 20px;border-radius:18px;border:1px solid rgba(245,158,11,0.3);background:rgba(245,158,11,0.1);color:#fff;font-size:15px;font-weight:700;cursor:pointer;width:100%;transition:all 0.25s;margin-top:10px;" onmouseover="this.style.background='rgba(245,158,11,0.2)';this.style.transform='translateY(-2px)'" onmouseout="this.style.background='rgba(245,158,11,0.1)';this.style.transform=''">
                <div style="width:40px;height:40px;background:rgba(245,158,11,0.2);border-radius:12px;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><i class="fa-solid fa-handshake" style="font-size:18px;color:#f59e0b;"></i></div>
                <div style="text-align:left;"><div style="font-size:15px;font-weight:700;">Loyihani Kelishish</div><div style="font-size:12px;opacity:0.7;font-weight:400;">Ustaga bildirishnoma yuborish</div></div>
            </button>`;
            
            if (isClient) {
                btns += `<button onclick="sendInterest(${userId})" style="display:flex;align-items:center;gap:14px;padding:16px 20px;border-radius:18px;border:1px solid rgba(236,72,153,0.3);background:rgba(236,72,153,0.1);color:#fff;font-size:15px;font-weight:700;cursor:pointer;width:100%;transition:all 0.25s;margin-top:10px;" onmouseover="this.style.background='rgba(236,72,153,0.2)';this.style.transform='translateY(-2px)'" onmouseout="this.style.background='rgba(236,72,153,0.1)';this.style.transform=''">
                    <div style="width:40px;height:40px;background:rgba(236,72,153,0.2);border-radius:12px;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><i class="fa-solid fa-heart" style="font-size:18px;color:#ec4899;"></i></div>
                    <div style="text-align:left;"><div style="font-size:15px;font-weight:700;">Qiziqish Bildirish</div><div style="font-size:12px;opacity:0.7;font-weight:400;">Xizmatlariga e'tibor qaratish</div></div>
                </button>`;
            }
        }
"""

# Helper functions
extra_funcs = """
async function sendNegotiate(userId) {
    closeContactModal();
    showToast('success', 'Yuborilmoqda...');
    try {
        const lang = window.location.pathname.split('/')[1] || 'uz';
        const res = await fetch(`/${lang}/api/user/${userId}/negotiate/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': '{{ csrf_token }}', 'Content-Type': 'application/json' }
        });
        const d = await res.json();
        if (res.ok) { showToast('success', d.message); } 
        else { showToast('error', d.error || 'Xatolik yuz berdi'); }
    } catch(e) { showToast('error', 'Tarmoq xatosi'); }
}

async function sendInterest(userId) {
    closeContactModal();
    showToast('success', 'Yuborilmoqda...');
    try {
        const lang = window.location.pathname.split('/')[1] || 'uz';
        const res = await fetch(`/${lang}/api/user/${userId}/interest/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': '{{ csrf_token }}', 'Content-Type': 'application/json' }
        });
        const d = await res.json();
        if (res.ok) { showToast('success', d.message); } 
        else { showToast('error', d.error || 'Xatolik yuz berdi'); }
    } catch(e) { showToast('error', 'Tarmoq xatosi'); }
}
"""

for f in ['templates/build/home.html', 'templates/build/network.html', 'templates/build/builder_list.html', 'templates/build/dashboard.html']:
    with open(f, 'r') as file:
        content = file.read()
        
    if "sendNegotiate" not in content:
        # Inject buttons in contactUser
        target = "if (!d.phone && !d.telegram && !d.whatsapp && !d.instagram && !d.facebook)"
        content = content.replace(target, extra_js + "\n        " + target)
        
        # Inject functions
        target_func = "function closeContactModal()"
        content = content.replace(target_func, extra_funcs + "\n" + target_func)
        
        with open(f, 'w') as file:
            file.write(content)
        print(f"Injected in {f}")

