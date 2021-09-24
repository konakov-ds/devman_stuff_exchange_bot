import os
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update, keyboardbutton
from telegram.ext import MessageHandler, CommandHandler, Updater, Filters, ConversationHandler
from dotenv import load_dotenv


load_dotenv()
# Загружаем токен для телеграм бота
token = os.getenv('TELEGRAM_TOKEN')

PHOTO, NAME = range(2)

is_authorisation = False

categories = [
    '🚖 Транспорт',
    '👔 Одежда, обувь',
    '💍 Аксессуары и украшения',
    '👕 Детская одежда и обувь',
    '🧸 Игрушки и детские транспортвещи',
    '📺 Бытовая техника',
    '🛋 Мебель и интерьерные вещи',
    '🍲 Кухонная утварь',
    '🥕 Продукты питания',
    '🏗 Вещи для ремонта и строительства',
    '☘ Растения',
    '💻 Электроника',
    '🏸 Спортивные вещи',
    '🎨 Вещи для творчества и хобби',
    '🏆 Коллекционные вещи'
 ]


def main_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='✅ Добавить вещь'),
                KeyboardButton(text='🔍 Найти вещь')
            ],
        ],
        resize_keyboard=True
    )
    return markup


def first_category_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='🚖 Транспорт'),
                KeyboardButton(text='👔 Одежда, обувь'),
            ],
            [
                KeyboardButton(text='💍 Аксессуары и украшения'),
                KeyboardButton(text='👕 Детская одежда и обувь'),               
            ],
            [
                KeyboardButton(text='🧸 Игрушки и детские транспортвещи'),
                KeyboardButton(text='📺 Бытовая техника'),               
            ],
            [
                KeyboardButton(text='🛋 Мебель и интерьерные вещи'),
                KeyboardButton(text='🍲 Кухонная утварь'),               
            ],
            [
                KeyboardButton(text='🔁 На главную'),
                KeyboardButton(text='➡ Вперед'),               
            ],
        ],
        resize_keyboard=True
    )
    return markup


def second_category_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='🥕 Продукты питания'),
                KeyboardButton(text='🏗 Вещи для ремонта и строительства'),
            ],
            [
                KeyboardButton(text='☘ Растения'),
                KeyboardButton(text='💻 Электроника'),               
            ],
            [
                KeyboardButton(text='🏸 Спортивные вещи'),
                KeyboardButton(text='🎨 Вещи для творчества и хобби'),               
            ],
            [
                KeyboardButton(text='🏆 Коллекционные вещи'),        
            ],
            [
                KeyboardButton(text='🔁 На главную'),
                KeyboardButton(text='⬅ Назад'),               
            ],
        ],
        resize_keyboard=True
    )
    return markup


def cancel_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='❌ Отменить'),               
            ],
        ],
        resize_keyboard=True
    )
    return markup


def find_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='🔍 Найти вещь'),
                KeyboardButton(text='👍 Нравится'),
                KeyboardButton(text='👏 Предложить обмен'),             
            ],
            [
                KeyboardButton(text='🔁 На главную'),
            ]
        ],
        resize_keyboard=True
    )
    return markup


def start_bot(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет!\nЯ бот для обмена вещей.\nВыбери нужный пункт в меню.",
        reply_markup=main_keyboard(),
    )


def select_category_handler(update, context):
    if update.message.text == '✅ Добавить вещь':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы на первой странице категорий',
            reply_markup=first_category_keyboard(),
        )
    elif update.message.text == '➡ Вперед':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы на второй странице категорий',
            reply_markup=second_category_keyboard()
        )
    elif update.message.text == '⬅ Назад':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы на первой странице категорий',
            reply_markup=first_category_keyboard()
        )
    elif update.message.text == '🔁 На главную':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Выберите пункт меню.',
            reply_markup=main_keyboard()
        )


def find_thing_handler(update, context):
    if update.message.text == '🔍 Найти вещь':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Показана случайная вещь из базы бота.',
            reply_markup=finde_keybord()
        )
    elif update.message.text == '🔁 На главную':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Выберите пункт меню.',
            reply_markup=main_keyboard()
        )


def name_category_handler(update, context):
    if update.message.text in categories:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Отправьте фото вещи.',
            reply_markup=cancel_keyboard()
        )
        return PHOTO


def photo_handler(update, context):
    if update.message.photo[-1]:
        file = update.message.photo[-1].get_file()
        file.download()
        context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Фото получено.\nОтправьте название вещи.',
                reply_markup=cancel_keyboard()
            )
        return NAME


def name_thing_handler(update, context):
    if update.message.text != '❌ Отменить':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Название вещи получено!\n{update.message.text} добавлено в базу.',
            reply_markup=main_keyboard()
        )
        return ConversationHandler.END


def cancel_handler(update: Update, context):
    if update.message.text == '❌ Отменить':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Вы отменили размещение вещи. Чтобы начать заново отправьте /start',
            reply_markup=main_keyboard()
        )
        return ConversationHandler.END


def main():
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.text(categories), name_category_handler),
        ],
        states={
            PHOTO: [
                MessageHandler(Filters.photo, photo_handler, pass_user_data=True),
            ],
            NAME: [
                MessageHandler(Filters.text, name_thing_handler, pass_user_data=True),
            ]
        },
        fallbacks=[
            MessageHandler(Filters.text, cancel_handler),
        ],
    )

    dispatcher.add_handler(CommandHandler('start', start_bot))

    dispatcher.add_handler(conv_handler)

    dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=select_category_handler))

    dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=find_thing_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()