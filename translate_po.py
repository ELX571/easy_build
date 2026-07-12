import re

translations = {
    "Bildirishnomalar": "Уведомления",
    "EasyBuild Premium": "EasyBuild Premium",
    "Yangi buyurtmalar": "Новые заказы",
    "Tizim xabarnomalari": "Системные уведомления",
    "Aksiya va chegirmalar": "Акции и скидки",
    "Premium obunachi": "Премиум подписчик",
    "O'rtacha baho": "Средняя оценка",
    "Tugatilgan buyurtmalar": "Завершенные заказы",
    "Bekor qilingan buyurtmalar": "Отмененные заказы",
    "O'rtacha javob berish vaqti (daqiqa)": "Среднее время ответа (минуты)",
    "Sarlavha": "Заголовок",
    "Havola (URL)": "Ссылка (URL)",
    "O'qilgan": "Прочитано",
    "O'zingizning ma'lumotlaringiz.": "Ваши данные.",
    "Kompaniya/Jamoa": "Компания/Команда",
    "O'zingizni qo'sha olmaysiz!": "Вы не можете добавить себя!",
    "Foydalanuvchi eng ko'pi bilan 2 ta jamoaga a'zo bo'lishi mumkin!": "Пользователь может состоять максимум в 2 командах!",
    "Taklif allaqachon yuborilgan!": "Приглашение уже отправлено!",
    "Taklif foydalanuvchi chatiga yuborildi!": "Приглашение отправлено в чат пользователя!",
    "Sizga tegishli taklif emas!": "Это предложение не для вас!",
    "Siz eng ko'pi bilan 2 ta jamoaga a'zo bo'lishingiz mumkin!": "Вы можете состоять максимум в 2 командах!",
    "🤝 Men jamoangizga qo'shilish taklifini qabul qildim!": "🤝 Я принял приглашение присоединиться к вашей команде!",
    "🚀 {name} Jamoasi": "🚀 Команда {name}",
    "❌ Men jamoangizga qo'shilish taklifini rad etdim.": "❌ Я отклонил приглашение присоединиться к вашей команде.",
    "Taklif rad etildi!": "Приглашение отклонено!",
    "Noto'g'ri so'rov.": "Неверный запрос.",
    "Jamoa nomi kiritilmagan!": "Название команды не введено!",
    "Русский": "Русский",
    "English": "English",
    "Premium Obuna": "Премиум подписка",
    "Kalit so'z / Ism": "Ключевое слово / Имя",
    "Usta ismi yoki kalit so\\": "Имя мастера или ключевое слово\\",
    "Elektrik": "Электрик",
    "Santexnik": "Сантехник",
    "Betonchi / Armaturachi": "Бетонщик / Арматурщик",
    "Suvoqchi / Malyar": "Штукатур / Маляр",
    "Kafelchi (Plitkach)": "Кафельщик (Плиточник)",
    "Payvandchi (Svarshik)": "Сварщик",
    "Tom yopuvchi (Tomchi)": "Кровельщик",
    "G'isht quyuvchi (G'ishtchi)": "Каменщик",
    "Duradgor / Yog'och ustasi": "Плотник / Столяр",
    "Gipsokartonchi": "Гипсокартонщик",
    "Isitish va Sovutish (HVAC)": "Отопление и охлаждение (HVAC)",
    "Loyiha muhandisi (Prorab)": "Прораб",
    "Fasad ustasi": "Мастер по фасадам",
    "Demontaj / Buzish ishlari": "Демонтаж",
    "Umumiy quruvchi": "Разнорабочий",
    "Minimal Reyting": "Минимальный рейтинг",
    "Premium": "Премиум",
    "Yuqori": "Высокий",
    "Yaxshi": "Хороший",
    "Gamifikatsiya": "Геймификация",
    "Reyting": "Рейтинг",
    "Qidiruv shartlariga mos keladigan Quruvchilar hozircha mavjud emas.": "Строителей, соответствующих условиям поиска, пока нет.",
    "Kerakli e\\": "Нужное об\\",
    "Rasm yuklash:": "Загрузить фото:",
    "Ortga": "Назад",
    "Sizda yangi bildirishnomalar yo'q.": "У вас нет новых уведомлений.",
    "Hudud": "Регион",
    "Men haqimda (Bio)": "Обо мне (Bio)",
    "Sizga qanday bildirishnomalar kelishini boshqaring.": "Управляйте тем, какие уведомления вам приходят.",
    "Birov sizga xabar yozganda email orqali bildirishnoma jo'natish": "Отправлять уведомление по email, когда вам пишут сообщение",
    "Sizga yangi ish taklif qilinganda xabarnoma jo'natish": "Отправлять уведомление, когда вам предлагают новую работу",
    "EasyBuild tizimidagi chegirmalar, yangiliklar va maxsus takliflar": "Скидки, новости и специальные предложения в системе EasyBuild",
    "Men a'zo bo'lgan jamoalar": "Команды, в которых я состою",
}

with open('locale/ru/LC_MESSAGES/django.po', 'r') as f:
    content = f.read()

for uz, ru in translations.items():
    # We replace msgid "uz"\nmsgstr "" with msgid "uz"\nmsgstr "ru"
    pattern = r'msgid "' + re.escape(uz) + r'"\nmsgstr ""'
    replacement = 'msgid "' + uz + '"\nmsgstr "' + ru + '"'
    content = re.sub(pattern, replacement, content)

# A couple multi-line strings
content = content.replace(
    '"bo\'lmaydi."\nmsgstr ""', 
    '"bo\'lmaydi."\nmsgstr "Это действие нельзя отменить."'
)
content = content.replace(
    '"mumkin (Tez kunda ishga tushadi)."\nmsgstr ""',
    '"mumkin (Tez kunda ishga tushadi)."\nmsgstr "Здесь вы можете изменить свой пароль или настройки безопасности (Скоро будет доступно)."'
)

with open('locale/ru/LC_MESSAGES/django.po', 'w') as f:
    f.write(content)

print("Translations applied successfully!")
