from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    ReplyKeyboardRemove,
)
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import random, os

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

EVENTS = [
    "18.01.25 - Ночная репетиция, время: 22:00",
    "25.01.25 - Ночная репетиция, время: 22:00",
    "01.02.25 - Ночная репетиция, время: 22:00",
]

MEMS = [
    "https://i.pinimg.com/736x/a1/8b/06/a18b063a4a1bfdd5fb53afddb3616043.jpg",
    "https://i.pinimg.com/736x/01/5c/16/015c16993ae37a337e212c931fe90ca8.jpg",
    "https://i.pinimg.com/736x/6b/bf/22/6bbf22ae7a4f4ca9d4115b64e2b2e22d.jpg",
    "https://i.pinimg.com/736x/b3/8e/69/b38e69bd410e31b0f3c2f06e6e510307.jpg",
    "https://i.pinimg.com/736x/a5/a9/d9/a5a9d91e35e262242027fe07b991031c.jpg",
    "https://i.pinimg.com/736x/72/fc/ed/72fced4b72d020e7a371095ce4209698.jpg",
    "https://i.pinimg.com/736x/84/72/05/847205e7fbb4dc8a6bd396e7bdc80847.jpg",
    "https://i.pinimg.com/736x/13/48/b6/1348b6d619cb54043813821577f15b2e.jpg",
    "https://i.pinimg.com/736x/5b/b7/2e/5bb72ec359a6ecc7811f80124ce7d635.jpg",
    "https://i.pinimg.com/736x/f8/4d/f4/f84df46aa202e2a40356b33fc3ac7847.jpg",
]

TELEGRAM_USER = "1493688059"
TELEGRAM_TOKEN = "7619104440:AAHdFpaYtoCS6pE3B9Ii8WJjU0KaR4YxVFA"
EDIT_MODE = None 
URL = "https://"

async def set_webhook() -> None:
    # Укажите URL вашего бота
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    success = await application.bot.set_webhook(URL)
    if success:
        print("Webhook установлен успешно!")
    else:
        print("Ошибка при установке вебхука.")

# Функция для создания основного меню
def get_main_menu():
    keyboard = [
        ["Список кандидатов", "Контакты", "Ваши предложения"],  
        ["Задачи на неделю от командного состава"],
        ["Календарь мероприятий", "Жизненый или милый мем"],  
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Функция для создания inline-кнопок
def get_return_button():
    keyboard = [[InlineKeyboardButton("Возврат к меню", callback_data="return_to_menu")]]
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
        await update.message.reply_text("Группа ВК: https://vk.com/osd_sibhar \nТелеграмм канал: https://t.me/osd_sibhar \nГлавный разработчик(ТГ аккаунт): @FistQunami")
    elif user_message == "Задачи на неделю от командного состава":
        await update.message.reply_text(f"Задачи на неделю:\n{ZADACHI_INFO}", disable_web_page_preview=True)
    elif user_message == "Ваши предложения":
        await handle_suggestions_start(update, context)
    elif user_message == "Календарь мероприятий":
        await calendar(update, context)
    elif user_message == "Жизненый или милый мем":
        await meme_of_the_day(update, context)
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

async def meme_of_the_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправить случайный мем."""
    if MEMS:
        meme_url = random.choice(MEMS)
        await update.message.reply_photo(photo=meme_url)
    else:
        await update.message.reply_text("Извините, сейчас мемов нет.")

# Режим редактирования для админа
async def handle_admin_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global EDIT_MODE, EVENTS, ZADACHI_INFO, MEMS

    new_text = update.message.text

    if EDIT_MODE == "EVENTS":
        EVENTS.append(new_text)
        await update.message.reply_text("Событие добавлено в календарь!", reply_markup=get_main_menu())
    elif EDIT_MODE == "TASKS":
        ZADACHI_INFO = new_text
        await update.message.reply_text("Задачи недели обновлены!", reply_markup=get_main_menu())
    elif EDIT_MODE == "ADD_MEME":
        new_meme = update.message.text
        MEMS.append(new_meme)
        await update.message.reply_text("Мем добавлен!", reply_markup=get_main_menu())
        EDIT_MODE = None

    EDIT_MODE = None

# Обработчик команды /edit_tasks
async def edit_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global EDIT_MODE
    EDIT_MODE = "TASKS"
    await update.message.reply_text("Введите новые задачи на неделю:", reply_markup=ReplyKeyboardRemove())

# Обработчик команды /edit_calendar
async def edit_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global EDIT_MODE
    EDIT_MODE = "EVENTS"
    await update.message.reply_text("Введите новое событие для календаря:", reply_markup=ReplyKeyboardRemove())

async def add_meme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Добавить новый мем в список (только для админа)."""
    global EDIT_MODE
    if str(update.effective_user.id) == TELEGRAM_USER:
        EDIT_MODE = "ADD_MEME"
        await update.message.reply_text("Отправьте URL нового мема:", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")

# Календарь событий
async def calendar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = "\n".join(EVENTS)
    await update.message.reply_text(f"Календарь мероприятий:\n{message}")

def main():
    bot_token = "7619104440:AAHdFpaYtoCS6pE3B9Ii8WJjU0KaR4YxVFA"
    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("edit_calendar", edit_calendar))
    app.add_handler(CommandHandler("edit_tasks", edit_tasks))
    app.add_handler(CommandHandler("add_meme", add_meme))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("calendar", calendar))

    app.run_polling()

if __name__ == "__main__":
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрация команды /start
    application.add_handler(CommandHandler("start", start))

    # Запуск вебхука и переключение в режим pollings
    application.run_polling()
    main()

