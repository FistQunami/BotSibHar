from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import random, requests 
from bs4 import BeautifulSoup

CANDIDATES_INFO = """
1. Чернявская Алина Игоревна
   День рождения: 25.05.2004, 
   Полных лет: 20, 
   Номер телефона: 89230487956
2. Дудник Софья Сергеевна
   День рождения: 03.05.2004, 
   Полных лет: 20, 
   Номер телефона: 89026765358
3. Кочетов Константин Олегович
   День рождения: 19.11.2006, 
   Полных лет: 18, 
   Номер телефона: 89681076793
4. Мушинская Мирослава Олеговна
   День рождения: 23.02.2004, 
   Полных лет: 20, 
   Номер телефона: 89081191020
5. Дербенева Екатерина Алексеевна 
   День рождения: 04.04.2003, 
   Полных лет: 21, 
   Номер телефона: 89237686602
6. -
7. Арсонов Даниил Дмитриевич
   День рождения: 07.01.2007, 
   Полных лет: 18, 
   Номер телефона: 89952741653
8. Павлович Ольга Константиновна
   День рождения: 30.04.2005, 
   Полных лет: 19, 
   Номер телефона: 89514194078
9. Валл Татьяна Викторовна
   День рождения: 21.06.2005, 
   Полных лет: 19, 
   Номер телефона: 89040729708
10. Белеява Татьяна Валерьевна
   День рождения: 07.01.2002, 
   Полных лет: 23, 
   Номер телефона: 89521605731
"""

ZADACHI_INFO = """13.01.25-19.01.25:
1. Принести весь реквизит и костюмы на репетицию.
2. ВСЕМ ЗАПОЛНИТЬ ТАБЛИЦУ. Дедлайн: до 18:00 Субботы (18.01.25).
Заполняйте максимально подробно! Обратите внимание на таблицу «ОБЩЕЕ БЛАГО», разбирайте пункты оттуда!
[Ссылка на таблицу](https://docs.google.com/spreadsheets/d/1sDnJk6gU4I1cbCagWUNymxGUQKUv7xy52OWJzTLkyyQ/edit#gid=0).
"""

FACTS = [
    "Улыбка - ваш лучший инструмент для команды!",
    "Помните, что хороший план важнее хаотичной импровизации.",
    "Чай с коллегой порой важнее миллионного отчета.",
]

EVENTS = [
    "18.01.25 - Ночная репетиция, время: 22:00",
    "25.01.25 - Ночная репетиция, время: 22:00",
    "01.02.25 - Ночная репетиция, время: 22:00",
]

SIGN_TRANSLATION = {
    "овен": "aries",
    "телец": "taurus",
    "близнецы": "gemini",
    "рак": "cancer",
    "лев": "leo",
    "дева": "virgo",
    "весы": "libra",
    "скорпион": "scorpio",
    "стрелец": "sagittarius",
    "козерог": "capricorn",
    "водолей": "aquarius",
    "рыбы": "pisces"
}

TELEGRAM_USER = "1493688059"
EDIT_MODE = None  # Глобальная переменная для определения текущего режима редактирования

# Функция для создания основного меню
def get_main_menu():
    keyboard = [
        ["Список кандидатов", "Контакты", "Ваши предложения"],  
        ["Задачи на неделю от командного состава"],
        ["Календарь мероприятий", "Гороскоп дня"],  
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Функция для создания inline-кнопок
def get_return_button():
    keyboard = [[InlineKeyboardButton("Возврат к меню", callback_data="return_to_menu")]]
    return InlineKeyboardMarkup(keyboard)

def get_horoscope_menu():
    zodiac_signs = [
        "Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", 
        "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"
    ]
    keyboard = [[InlineKeyboardButton(sign, callback_data=f"horoscope_{sign}")] for sign in zodiac_signs]
    return InlineKeyboardMarkup(keyboard)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name or "Гость"
    await update.message.reply_text(
        f"Приветствуем в нашем боте, {user_name}!\n\n"
        f"Выберите из меню, что вас интересует:",
        reply_markup=get_main_menu(),
    )
    context.user_data["waiting_for_suggestions"] = False

# Обработчик текста из меню
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global EDIT_MODE

    user_message = update.message.text
    if EDIT_MODE:
        await handle_admin_edit(update, context)
        return

    if context.user_data.get("waiting_for_suggestions"):
        await handle_suggestions_message(update, context)
        return

    if user_message == "Список кандидатов":
        await update.message.reply_text(f"Список кандидатов:\n{CANDIDATES_INFO}")
    elif user_message == "Контакты":
        await update.message.reply_text("Связь с нами: aboba228@rambler.com")
    elif user_message == "Задачи на неделю от командного состава":
        await update.message.reply_text(f"Задачи на неделю:\n{ZADACHI_INFO}", disable_web_page_preview=True)
    elif user_message == "Ваши предложения":
        await handle_suggestions_start(update, context)
    elif user_message == "Календарь мероприятий":
        await calendar(update, context)
    elif user_message == "Гороскоп дня":
        await horoscope(update, context)
    else:
        await update.message.reply_text("Пожалуйста, выберите команду из меню.", reply_markup=get_main_menu())

# Обработчик входа в режим предложений
async def handle_suggestions_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Можете написать ваши предложения по поводу улучшения бота, если заметили ошибки или просто что-нибудь милое. "
        "Для возврата к основному меню нажмите на кнопку под сообщением.",
        reply_markup=get_return_button(),
    )
    context.user_data["waiting_for_suggestions"] = True
    await update.message.reply_text("Введите предложение:", reply_markup=ReplyKeyboardRemove())

# Обработчик предложений
async def handle_suggestions_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_suggestion = update.message.text
    try:
        await context.bot.send_message(
            chat_id=TELEGRAM_USER,
            text=f"Новое предложение от @{update.effective_user.username or 'анонимного пользователя'}:\n{user_suggestion}",
        )
        await update.message.reply_text(
            "Спасибо за ваше предложение! Для возврата к основному меню нажмите на кнопку ниже.",
            reply_markup=get_return_button(),
        )
        context.user_data["waiting_for_suggestions"] = False
    except BadRequest as e:
        await update.message.reply_text(
            "Ошибка отправки сообщения. Убедитесь, что конфигурация чата верна.",
            reply_markup=get_return_button(),
        )
        print(f"Ошибка при отправке сообщения: {e}")

# Обработчик кнопки возврата
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "return_to_menu":
        await query.message.reply_text(
            "Возвращаемся в главное меню...", reply_markup=get_main_menu()
        )
        context.user_data["waiting_for_suggestions"] = False

# Режим редактирования для админа
async def handle_admin_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global EDIT_MODE, FACTS, EVENTS

    new_text = update.message.text

    if EDIT_MODE == "FACTS":
        FACTS.append(new_text)
        await update.message.reply_text("Цитата добавлена!", reply_markup=get_main_menu())
    elif EDIT_MODE == "EVENTS":
        EVENTS.append(new_text)
        await update.message.reply_text("Событие добавлено в календарь!", reply_markup=get_main_menu())

    EDIT_MODE = None

# Обработчик команды /edit_facts
async def edit_facts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global EDIT_MODE
    EDIT_MODE = "FACTS"
    await update.message.reply_text("Введите новую цитату дня:", reply_markup=ReplyKeyboardRemove())

# Обработчик команды /edit_calendar
async def edit_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global EDIT_MODE
    EDIT_MODE = "EVENTS"
    await update.message.reply_text("Введите новое событие для календаря:", reply_markup=ReplyKeyboardRemove())

# Календарь событий
async def calendar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = "\n".join(EVENTS)
    await update.message.reply_text(f"Календарь мероприятий:\n{message}")

async def horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Выберите ваш знак зодиака:",
        reply_markup=get_horoscope_menu()
    )

async def handle_horoscope_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    selected_sign = query.data.replace("horoscope_", "").lower()
    translated_sign = SIGN_TRANSLATION.get(selected_sign)

    if not translated_sign:
        await query.message.reply_text(
            f"Не удалось найти гороскоп для знака {selected_sign}.",
            reply_markup=get_main_menu(),
        )
        return

    horoscope_url = f"https://horo.mail.ru/prediction/{translated_sign}/today/"

    try:
        response = requests.get(horoscope_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Найти текст гороскопа
        horoscope_block = soup.find("div", class_="article__item article__item_alignment_left article__item_html")
        horoscope_text = horoscope_block.text.strip() if horoscope_block else "Гороскоп не найден."

        await query.message.reply_text(
            f"Гороскоп для знака {selected_sign}:\n\n{horoscope_text}",
            reply_markup=get_main_menu(),
        )
    except requests.exceptions.RequestException as e:
        await query.message.reply_text(
            f"Не удалось получить гороскоп для {selected_sign}. Попробуйте позже.",
            reply_markup=get_main_menu(),
        )
        print(f"Ошибка при запросе гороскопа: {e}")

async def fetch_website_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = "https://horo.mail.ru"  # Укажите URL
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка успешности запроса
        content = response.text  # Если это HTML
        # Если возвращается JSON:
        # content = response.json()

        await update.message.reply_text(f"Данные с сайта:\n{content}")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text("Не удалось загрузить данные с сайта.")
        print(f"Ошибка запроса: {e}")

def main():
    bot_token = "7619104440:AAHdFpaYtoCS6pE3B9Ii8WJjU0KaR4YxVFA"
    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("fetch_content", fetch_website_content))  # Новый обработчик
    app.add_handler(CallbackQueryHandler(handle_horoscope_selection, pattern=r"^horoscope_"))
    app.add_handler(CommandHandler("edit_facts", edit_facts))
    app.add_handler(CommandHandler("edit_calendar", edit_calendar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("calendar", calendar))
    app.add_handler(CommandHandler("horoscope", horoscope))

    app.run_polling()

if __name__ == "__main__":
    main()

