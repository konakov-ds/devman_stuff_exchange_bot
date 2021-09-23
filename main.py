import os
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import MessageHandler, CommandHandler, Updater, Filters, CallbackContext
from dotenv import load_dotenv

load_dotenv()
# Загружаем токен для телеграм бота
token = os.getenv('TELEGRAM_TOKEN')

categories = ['Транспорт',
              'Одежда, обувь',
              'Аксессуары и украшения',
              'Детская одежда и обувь',
              'Игрушки и детские транспортвещи',
              'Бытовая техника',
              'Мебель и интерьерные вещи',
              'Кухонная утварь',
              'Продукты питания',
              'Вещи для ремонта и строительства',
              'Растения',
              'Электроника',
              'Спортивные вещи',
              'Вещи для творчества и хобби',
              'Коллекционные вещи'
              ]


def create_main_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Добавить вещь'),
                KeyboardButton(text='Найти вещь'),
                KeyboardButton(text='Обменяться')
            ],
        ],
        resize_keyboard=True
    )
    return markup


def create_add_item_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Выберите категорию'),
                KeyboardButton(text='Добавьте фото'),
                KeyboardButton(text='Добавьте название')
                ,
            ],
            [
                KeyboardButton(text='Вернуться в главное меню')
            ]
        ],
        resize_keyboard=True
    )
    return markup


def create_category_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=category) for category in categories[i: i + 2]
            ]
            for i in range(0, len(categories) - 2, 2)
        ],
        resize_keyboard=True
    )
    return markup


def start_bot(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет!\nЯ бот для обмена вещей.\nВыбери нужный пункт в меню.",
        reply_markup=create_main_keyboard(),
    )


def bot_help(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Справка по работе с ботом для обмена вещей.",
    )


def button_message_handler(update, context):
    if update.message.text == 'Добавить вещь':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выбери нужный пункт в меню.",
            reply_markup=create_add_item_keyboard(),
        )
    elif update.message.text == 'Вернуться в главное меню':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы вернулись в главное меню',
            reply_markup=create_main_keyboard(),
        )
    elif update.message.text == 'Выберите категорию':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выбери категорию",
            reply_markup=create_category_keyboard(),
        )
    elif update.message.text in categories:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Вы выбрали {update.message.text}",
            reply_markup=create_add_item_keyboard(),
        )
    elif update.message.text == 'Добавьте фото':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Загрузите фото",
            reply_markup=create_add_item_keyboard(),
        )

    elif update.message.text == 'Добавьте название':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Напишите название вашей вещи",
            reply_markup=create_add_item_keyboard(),
        )
    elif update.message.text == 'Найти вещь':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='[ФОТО]',
            reply_markup=create_main_keyboard(),
        )
    elif update.message.text == 'Обменяться':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='[КОНТАКТЫ ДЛЯ ОБМЕНА]',
            reply_markup=create_main_keyboard(),
        )


def photo_handler(update, context):
    file = update.message.document
    obj = context.bot.get_file(file['file_id'])
    # print(file)
    obj.download()
    update.message.reply_text("Фото получено")


def main():
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start_bot))
    dispatcher.add_handler(CommandHandler('help', bot_help))
    dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=button_message_handler))
    dispatcher.add_handler(MessageHandler(filters=Filters.document, callback=photo_handler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()