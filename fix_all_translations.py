import re
import os
import subprocess

html_path = 'templates/build/profile_edit.html'
with open(html_path, 'r') as f:
    content = f.read()

replacements = {
    ">Joriy Tarfingiz<": ">{% trans \"Joriy Ta'rifingiz\" %}<",
    ">Cheksiz<": ">{% trans \"Cheksiz\" %}<",
    ">Asosiy imkoniyatlar<": ">{% trans \"Asosiy imkoniyatlar\" %}<",
    " Yangilash": " {% trans \"Yangilash\" %}",
    ">Oylik<": ">{% trans \"Oylik\" %}<",
    ">Yillik <": ">{% trans \"Yillik\" %} <",
    ">-20% foyda<": ">{% trans \"-20% foyda\" %}<",
    ">SINOV MUDDATI<": ">{% trans \"SINOV MUDDATI\" %}<",
    ">Chat orqali muloqot<": ">{% trans \"Chat orqali muloqot\" %}<",
    ">SINOV MUDDATI barcha funksiyalari<": ">{% trans \"SINOV MUDDATI barcha funksiyalari\" %}<",
    ">Sotib olish<": ">{% trans \"Sotib olish\" %}<",
    ">TOP USTALARGA<": ">{% trans \"TOP USTALARGA\" %}<",
    ">Sotuvda yo'q<": ">{% trans \"Sotuvda yo'q\" %}<",
    ">Saqlash<": ">{% trans \"Saqlash\" %}<",
    "> A'zo qo'shish<": "> {% trans \"A'zo qo'shish\" %}<",
    ">Qurilish jamoasi<": ">{% trans \"Qurilish jamoasi\" %}<",
    "> JAMOADAN O'CHIRISH<": "> {% trans \"JAMOADAN O'CHIRISH\" %}<",
    ">Jamoa sardori<": ">{% trans \"Jamoa sardori\" %}<",
    "> Faol a'zo<": "> {% trans \"Faol a'zo\" %}<",
    "> Yangi a'zo qo'shish<": "> {% trans \"Yangi a'zo qo'shish\" %}<",
    "> Taklif<": "> {% trans \"Taklif\" %}<",
    "> Yuborildi<": "> {% trans \"Yuborildi\" %}<",
    ">Barcha asosiy funksiyalar<": ">{% trans \"Barcha asosiy funksiyalar\" %}<",
    ">STANDARD ning barcha imkoniyatlari<": ">{% trans \"STANDARD ning barcha imkoniyatlari\" %}<",
    ">Admin tomonidan shaxsiy tavsiya etilish<": ">{% trans \"Admin tomonidan shaxsiy tavsiya etilish\" %}<",
    ">STANDARD<": ">{% trans \"STANDARD\" %}<",
    ">MAXSUS<": ">{% trans \"MAXSUS\" %}<",
    ">Faqat adminlar taqdim etadi<": ">{% trans \"Faqat adminlar taqdim etadi\" %}<",
    ">maqom<": ">{% trans \"maqom\" %}<"
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(html_path, 'w') as f:
    f.write(content)

print("HTML updated.")

# Run makemessages
subprocess.run(['.venv/bin/python', 'manage.py', 'makemessages', '-l', 'ru', '-l', 'en'], check=True)

translations_ru = {
    "Joriy Ta'rifingiz": "Ваш текущий тариф",
    "Cheksiz": "Безлимитно",
    "Asosiy imkoniyatlar": "Основные возможности",
    "Yangilash": "Обновить",
    "Oylik": "Ежемесячно",
    "Yillik": "Ежегодно",
    "-20% foyda": "-20% выгоды",
    "SINOV MUDDATI": "ПРОБНЫЙ ПЕРИОД",
    "Chat orqali muloqot": "Общение через чат",
    "SINOV MUDDATI barcha funksiyalari": "Все функции ПРОБНОГО ПЕРИОДА",
    "Sotib olish": "Купить",
    "TOP USTALARGA": "ТОП МАСТЕРАМ",
    "Sotuvda yo'q": "Нет в продаже",
    "Saqlash": "Сохранить",
    "A'zo qo'shish": "Добавить участника",
    "Qurilish jamoasi": "Строительная команда",
    "JAMOADAN O'CHIRISH": "УДАЛИТЬ ИЗ КОМАНДЫ",
    "Jamoa sardori": "Капитан команды",
    "Faol a'zo": "Активный участник",
    "Yangi a'zo qo'shish": "Добавить нового участника",
    "Taklif": "Пригласить",
    "Yuborildi": "Отправлено",
    "Barcha asosiy funksiyalar": "Все основные функции",
    "STANDARD ning barcha imkoniyatlari": "Все возможности STANDARD",
    "Admin tomonidan shaxsiy tavsiya etilish": "Личная рекомендация от админа",
    "STANDARD": "СТАНДАРТ",
    "MAXSUS": "СПЕЦИАЛЬНЫЙ",
    "Faqat adminlar taqdim etadi": "Выдается только админами",
    "maqom": "статус"
}

translations_en = {
    "Joriy Ta'rifingiz": "Your Current Plan",
    "Cheksiz": "Unlimited",
    "Asosiy imkoniyatlar": "Basic Features",
    "Yangilash": "Upgrade",
    "Oylik": "Monthly",
    "Yillik": "Yearly",
    "-20% foyda": "Save 20%",
    "SINOV MUDDATI": "TRIAL PERIOD",
    "Chat orqali muloqot": "Chat communication",
    "SINOV MUDDATI barcha funksiyalari": "All TRIAL PERIOD features",
    "Sotib olish": "Purchase",
    "TOP USTALARGA": "FOR TOP BUILDERS",
    "Sotuvda yo'q": "Not for sale",
    "Saqlash": "Save",
    "A'zo qo'shish": "Add Member",
    "Qurilish jamoasi": "Construction Team",
    "JAMOADAN O'CHIRISH": "REMOVE FROM TEAM",
    "Jamoa sardori": "Team Leader",
    "Faol a'zo": "Active Member",
    "Yangi a'zo qo'shish": "Add new member",
    "Taklif": "Invite",
    "Yuborildi": "Sent",
    "Barcha asosiy funksiyalar": "All core features",
    "STANDARD ning barcha imkoniyatlari": "All STANDARD features",
    "Admin tomonidan shaxsiy tavsiya etilish": "Personal recommendation from admin",
    "STANDARD": "STANDARD",
    "MAXSUS": "SPECIAL",
    "Faqat adminlar taqdim etadi": "Granted only by admins",
    "maqom": "status"
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
