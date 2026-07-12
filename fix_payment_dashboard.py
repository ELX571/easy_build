import re
import os
import subprocess

html_path = 'templates/build/payment_dashboard.html'
with open(html_path, 'r') as f:
    content = f.read()

replacements = {
    ">Nusxalash<": ">{% trans \"Nusxalash\" %}<",
    ">Kutilmoqda<": ">{% trans \"Kutilmoqda\" %}<",
    ">Tasdiqlandi<": ">{% trans \"Tasdiqlandi\" %}<",
    ">Rad etildi<": ">{% trans \"Rad etildi\" %}<",
    ">Vaqtinchalik 24 soatlik ruxsat faollashtirildi. Admin tasdig'ini kuting.<": ">{% trans \"Vaqtinchalik 24 soatlik ruxsat faollashtirildi. Admin tasdig'ini kuting.\" %}<",
    "Tarif tanlash va Tasdiqlash": "{% trans \"Tarif tanlash va Tasdiqlash\" %}",
    "Tarif paketini tanlang:": "{% trans \"Tarif paketini tanlang:\" %}",
    ">Maxsus<": ">{% trans \"Maxsus\" %}<",
    ">PRO Obuna<": ">{% trans \"PRO Obuna\" %}<",
    ">Premium VIP<": ">{% trans \"Premium VIP\" %}<",
    ">Faylni tanlang yoki shu yerga tashlang<": ">{% trans \"Faylni tanlang yoki shu yerga tashlang\" %}<",
    ">To'lovni tasdiqlash<": ">{% trans \"To'lovni tasdiqlash\" %}<",
    ">Premium Sotib Olish Chati<": ">{% trans \"Premium Sotib Olish Chati\" %}",
    ">Chatga xush kelibsiz<": ">{% trans \"Chatga xush kelibsiz\" %}<",
    ">Hozircha hech qanday to'lov so'rovi yubormagansiz.<": ">{% trans \"Hozircha hech qanday to'lov so'rovi yubormagansiz.\" %}<",
    "To'lov chekini yuklang (Screenshot):": "{% trans \"To'lov chekini yuklang (Screenshot):\" %}",
    "so'm": "{% trans \"so'm\" %}",
    "ENG ZO'R USTALAR UCHUN": "{% trans \"ENG ZO'R USTALAR UCHUN\" %}"
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(html_path, 'w') as f:
    f.write(content)

print("HTML updated.")

# Run makemessages
subprocess.run(['.venv/bin/python', 'manage.py', 'makemessages', '-l', 'ru', '-l', 'en'], check=True)

translations_ru = {
    "Nusxalash": "Копировать",
    "Kutilmoqda": "В ожидании",
    "Tasdiqlandi": "Подтверждено",
    "Rad etildi": "Отклонено",
    "Vaqtinchalik 24 soatlik ruxsat faollashtirildi. Admin tasdig'ini kuting.": "Временный доступ на 24 часа активирован. Ожидайте подтверждения админа.",
    "Tarif tanlash va Tasdiqlash": "Выбор тарифа и Подтверждение",
    "Tarif paketini tanlang:": "Выберите тарифный пакет:",
    "Maxsus": "Специальный",
    "PRO Obuna": "PRO Подписка",
    "Premium VIP": "Premium VIP",
    "Faylni tanlang yoki shu yerga tashlang": "Выберите файл или перетащите сюда",
    "To'lovni tasdiqlash": "Подтвердить оплату",
    "Premium Sotib Olish Chati": "Чат Покупки Premium",
    "Chatga xush kelibsiz": "Добро пожаловать в чат",
    "Hozircha hech qanday to'lov so'rovi yubormagansiz.": "Вы еще не отправляли запросов на оплату.",
    "To'lov chekini yuklang (Screenshot):": "Загрузите чек оплаты (Скриншот):",
    "so'm": "сум",
    "ENG ZO'R USTALAR UCHUN": "ДЛЯ САМЫХ ЛУЧШИХ МАСТЕРОВ"
}

translations_en = {
    "Nusxalash": "Copy",
    "Kutilmoqda": "Pending",
    "Tasdiqlandi": "Approved",
    "Rad etildi": "Rejected",
    "Vaqtinchalik 24 soatlik ruxsat faollashtirildi. Admin tasdig'ini kuting.": "Temporary 24-hour access activated. Wait for admin approval.",
    "Tarif tanlash va Tasdiqlash": "Plan Selection & Confirmation",
    "Tarif paketini tanlang:": "Select a subscription plan:",
    "Maxsus": "Special",
    "PRO Obuna": "PRO Subscription",
    "Premium VIP": "Premium VIP",
    "Faylni tanlang yoki shu yerga tashlang": "Select file or drop it here",
    "To'lovni tasdiqlash": "Confirm Payment",
    "Premium Sotib Olish Chati": "Premium Purchase Chat",
    "Chatga xush kelibsiz": "Welcome to the chat",
    "Hozircha hech qanday to'lov so'rovi yubormagansiz.": "You have not submitted any payment requests yet.",
    "To'lov chekini yuklang (Screenshot):": "Upload payment receipt (Screenshot):",
    "so'm": "UZS",
    "ENG ZO'R USTALAR UCHUN": "FOR TOP BUILDERS"
}

def apply_translations(lang_code, trans_dict):
    po_path = f'locale/{lang_code}/LC_MESSAGES/django.po'
    with open(po_path, 'r') as f:
        po_content = f.read()
    
    for uz, target in trans_dict.items():
        pattern = r'msgid "' + re.escape(uz) + r'"\nmsgstr ""'
        replacement = 'msgid "' + uz + '"\nmsgstr "' + target + '"'
        po_content = re.sub(pattern, replacement, po_content)
        
    with open(po_path, 'w') as f:
        f.write(po_content)

apply_translations('ru', translations_ru)
apply_translations('en', translations_en)
print("PO files updated.")

subprocess.run(['.venv/bin/python', 'manage.py', 'compilemessages'], check=True)
subprocess.run(['touch', 'conf/settings.py'], check=True)
print("Done.")
