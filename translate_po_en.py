import re

translations = {
    "Bildirishnomalar": "Notifications",
    "EasyBuild Premium": "EasyBuild Premium",
    "Yangi buyurtmalar": "New orders",
    "Tizim xabarnomalari": "System notifications",
    "Aksiya va chegirmalar": "Promotions and discounts",
    "Premium obunachi": "Premium subscriber",
    "O'rtacha baho": "Average rating",
    "Tugatilgan buyurtmalar": "Completed orders",
    "Bekor qilingan buyurtmalar": "Cancelled orders",
    "O'rtacha javob berish vaqti (daqiqa)": "Average response time (minutes)",
    "Sarlavha": "Title",
    "Havola (URL)": "Link (URL)",
    "O'qilgan": "Read",
    "O'zingizning ma'lumotlaringiz.": "Your data.",
    "Kompaniya/Jamoa": "Company/Team",
    "O'zingizni qo'sha olmaysiz!": "You cannot add yourself!",
    "Foydalanuvchi eng ko'pi bilan 2 ta jamoaga a'zo bo'lishi mumkin!": "User can be a member of maximum 2 teams!",
    "Taklif allaqachon yuborilgan!": "Invitation already sent!",
    "Taklif foydalanuvchi chatiga yuborildi!": "Invitation sent to user's chat!",
    "Sizga tegishli taklif emas!": "This offer is not for you!",
    "Siz eng ko'pi bilan 2 ta jamoaga a'zo bo'lishingiz mumkin!": "You can be a member of maximum 2 teams!",
    "🤝 Men jamoangizga qo'shilish taklifini qabul qildim!": "🤝 I accepted the invitation to join your team!",
    "🚀 {name} Jamoasi": "🚀 {name} Team",
    "❌ Men jamoangizga qo'shilish taklifini rad etdim.": "❌ I rejected the invitation to join your team.",
    "Taklif rad etildi!": "Invitation rejected!",
    "Noto'g'ri so'rov.": "Invalid request.",
    "Jamoa nomi kiritilmagan!": "Team name not entered!",
    "Русский": "Русский",
    "English": "English",
    "Premium Obuna": "Premium Subscription",
    "Kalit so'z / Ism": "Keyword / Name",
    "Usta ismi yoki kalit so\\": "Builder name or keyword\\",
    "Elektrik": "Electrician",
    "Santexnik": "Plumber",
    "Betonchi / Armaturachi": "Concrete worker / Rebar worker",
    "Suvoqchi / Malyar": "Plasterer / Painter",
    "Kafelchi (Plitkach)": "Tiler",
    "Payvandchi (Svarshik)": "Welder",
    "Tom yopuvchi (Tomchi)": "Roofer",
    "G'isht quyuvchi (G'ishtchi)": "Bricklayer",
    "Duradgor / Yog'och ustasi": "Carpenter",
    "Gipsokartonchi": "Drywaller",
    "Isitish va Sovutish (HVAC)": "Heating and Cooling (HVAC)",
    "Loyiha muhandisi (Prorab)": "Foreman",
    "Fasad ustasi": "Facade worker",
    "Demontaj / Buzish ishlari": "Demolition",
    "Umumiy quruvchi": "General Builder",
    "Minimal Reyting": "Minimum Rating",
    "Premium": "Premium",
    "Yuqori": "High",
    "Yaxshi": "Good",
    "Gamifikatsiya": "Gamification",
    "Reyting": "Rating",
    "Qidiruv shartlariga mos keladigan Quruvchilar hozircha mavjud emas.": "Builders matching the search criteria are not available yet.",
    "Kerakli e\\": "Required li\\",
    "Rasm yuklash:": "Upload image:",
    "Ortga": "Back",
    "Sizda yangi bildirishnomalar yo'q.": "You have no new notifications.",
    "Hudud": "Region",
    "Men haqimda (Bio)": "About me (Bio)",
    "Sizga qanday bildirishnomalar kelishini boshqaring.": "Manage which notifications you receive.",
    "Birov sizga xabar yozganda email orqali bildirishnoma jo'natish": "Send email notification when someone writes a message to you",
    "Sizga yangi ish taklif qilinganda xabarnoma jo'natish": "Send notification when you are offered a new job",
    "EasyBuild tizimidagi chegirmalar, yangiliklar va maxsus takliflar": "Discounts, news, and special offers in the EasyBuild system",
    "Men a'zo bo'lgan jamoalar": "Teams I belong to",
}

with open('locale/en/LC_MESSAGES/django.po', 'r') as f:
    content = f.read()

for uz, en in translations.items():
    pattern = r'msgid "' + re.escape(uz) + r'"\nmsgstr ""'
    replacement = 'msgid "' + uz + '"\nmsgstr "' + en + '"'
    content = re.sub(pattern, replacement, content)

content = content.replace(
    '"bo\'lmaydi."\nmsgstr ""', 
    '"bo\'lmaydi."\nmsgstr "This action cannot be undone."'
)
content = content.replace(
    '"mumkin (Tez kunda ishga tushadi)."\nmsgstr ""',
    '"mumkin (Tez kunda ishga tushadi)."\nmsgstr "Here you can change your password or security settings (Coming soon)."'
)

with open('locale/en/LC_MESSAGES/django.po', 'w') as f:
    f.write(content)

print("Translations applied successfully!")
