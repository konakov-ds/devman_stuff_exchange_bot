import os
from django.core.management.base import BaseCommand
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ConversationHandler, MessageHandler, CommandHandler, Updater, Filters, CallbackContext
from dotenv import load_dotenv
import random

from telbot.models import Profile, Message, Photo
from django.core.files import File

load_dotenv()
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


class Command(BaseCommand):
    help = 'Телеграм бот'

    def handle(self, *args, **kwargs):
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

        #dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=find_thing_handler))

        dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=select_category_handler))

        #dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=find))

        updater.start_polling()
        updater.idle()


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
    write_user_to_db(update)
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

    elif update.message.text == '🔍 Найти вещь':
        photo_path = get_photo_to_show(update)
        print(photo_path)
        send_photo_to_user(update, context, path=photo_path)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Показана случайная вещь из базы бота.',
            reply_markup=find_keyboard()
        )

    elif update.message.text == '👍 Нравится':
        write_liked_photo_to_db(update)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вам понравилось, отлично!',
            reply_markup=find_keyboard()
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
            reply_markup=find_keyboard()
        )
        photo_path = get_photo_to_show(update)
        print(photo_path)
        send_photo_to_user(update, context, path=photo_path)

    elif update.message.text == '🔁 На главную':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Выберите пункт меню.',
            reply_markup=main_keyboard()
        )


def name_category_handler(update, context):
    if update.message.text in categories:
        write_m_category_to_db(update)
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
        write_m_photo_to_db(update)
        get_photo_to_show(update)
        return NAME


def name_thing_handler(update, context):
    if update.message.text != '❌ Отменить':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Название вещи получено!\n{update.message.text} добавлено в базу.',
            reply_markup=main_keyboard()
        )
        write_m_name_to_db(update)
        return ConversationHandler.END


def cancel_handler(update: Update, context):
    if update.message.text == '❌ Отменить':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Вы отменили размещение вещи. Чтобы начать заново отправьте /start',
            reply_markup=main_keyboard()
        )
        return ConversationHandler.END


def write_user_to_db(update: Update):
    p, _ = Profile.objects.get_or_create(
            tg_id=update.effective_chat.id,
            defaults={
                'name': update.message.from_user.name,
            }
        )


def write_m_category_to_db(update: Update):
    p, _ = Profile.objects.get_or_create(
        tg_id=update.effective_chat.id,
        defaults={
            'name': update.message.from_user.name,
        }
    )
    Message.objects.create(
        profile=p,
        category=update.message.text
    )


def write_m_name_to_db(update: Update):
    p, _ = Profile.objects.get_or_create(
        tg_id=update.effective_chat.id,
        defaults={
            'name': update.message.from_user.name,
        }
    )
    last = Message.objects.filter(profile=p).last()
    print(last.id)
    Message(
        id=last.id,
        profile=p,
        category=last.category,
        name=update.message.text
    ).save()


def write_m_photo_to_db(update: Update):
    img_path = update.message.photo[-1].get_file()['file_path']
    img_path = img_path[img_path.find('file_'):]
    file_obj = File(open(img_path, mode='rb'), name='f1')
    photo, _ = Photo.objects.get_or_create(
        photo=file_obj
    )

    p, _ = Profile.objects.get_or_create(
        tg_id=update.effective_chat.id,

        defaults={
            'name': update.message.from_user.name,
        }
    )
    last = Message.objects.filter(profile=p).last()
    last.photo.add(photo)


random_photo = []


def write_liked_photo_to_db(update: Update):
    profile = Profile.objects.get(
        tg_id=update.effective_chat.id
    )
    profile.liked_stuff.add(random_photo[0])


def send_photo_to_user(update: Update, context, path):
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=path,
        reply_markup=main_keyboard()
    )


def get_photo_to_show(update: Update):
    exclude_profile = Profile.objects.get(tg_id=update.effective_chat.id)
    liked_stuff = Profile.objects.filter(liked_stuff__isnull=False).filter(tg_id=update.effective_chat.id)
    liked_stuff = [[j.photo for j in i.liked_stuff.all()] for i in liked_stuff.all()][0]
    #print(liked_stuff)

    messages = Message.objects.exclude(profile=exclude_profile)
    messages = messages.exclude(category__isnull=True).exclude(category__exact='')
    messages = messages.exclude(name__isnull=True).exclude(name__exact='')

    photos = Photo.objects.filter(photo__in=liked_stuff)
    #photos = Photo.objects.filter(message__in=messages)
    photo = random.choice(photos)
    random_photo.clear()
    random_photo.append(photo)
    return photo.photo