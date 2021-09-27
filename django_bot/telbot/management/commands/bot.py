import os
from collections import defaultdict
from django.core.management.base import BaseCommand
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update, user
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

random_photo = defaultdict()
random_photo_ex = defaultdict()


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


def main_keyboard(user_id):
    database_user_id = Profile.objects.filter(tg_id=user_id)
    active_user = Message.objects.filter(profile_id=database_user_id[0].id)
    if active_user.count() > 0:
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
    else:
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='✅ Добавить вещь'),
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
    user_id = update.effective_chat.id
    random_photo[update.effective_chat.id] = []
    random_photo_ex[update.effective_chat.id] = []
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет!\nЯ бот для обмена вещей.\nВыбери нужный пункт в меню.",
        reply_markup=main_keyboard(user_id),
    )


def select_category_handler(update, context):
    if update.message.text == '✅ Добавить вещь':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы на первой странице категорий',
            reply_markup=first_category_keyboard(),
        )

    elif update.message.text == '🔍 Найти вещь':
        photo_path, photo = get_photo_to_show(update)
        message = Message.objects.get(photo=photo)
        send_photo_to_user(update, context, path=photo_path)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Мы нашли для вас:\n{message.name}\nИз категории {message.category}',
            reply_markup=find_keyboard()
        )
        random_photo_ex[update.effective_chat.id].append(photo)

    elif update.message.text == '👍 Нравится':
        write_liked_photo_to_db(update)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вам понравилось, отлично!',
            reply_markup=find_keyboard()
        )

    elif update.message.text == '👏 Предложить обмен':
        write_exchange_photo_to_db(update)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Хорошая идея!\nМы проверим, готов ли владелец к обмену с вами',
            reply_markup=find_keyboard()
        )
        owner = get_owner_photo(update)
        exchange_users = get_to_exchange_users(owner)
        random_photo_ex[update.effective_chat.id].clear()
        if update.effective_chat.id in exchange_users:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Владелец {owner.name} готов к обмену',
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
        user_id = update.effective_chat.id
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Выберите пункт меню.',
            reply_markup=main_keyboard(user_id)
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
        user_id = update.effective_chat.id
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Выберите пункт меню.',
            reply_markup=main_keyboard(user_id)
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
        user_id = update.effective_chat.id
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Название вещи получено!\n{update.message.text} добавлено в базу.',
            reply_markup=main_keyboard(user_id)
        )
        write_m_name_to_db(update)
        return ConversationHandler.END


def cancel_handler(update, context):
    if update.message.text == '❌ Отменить':
        user_id = update.effective_chat.id
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Вы отменили размещение вещи. Чтобы начать заново отправьте /start',
            reply_markup=main_keyboard(user_id)
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


def write_liked_photo_to_db(update: Update):
    profile = Profile.objects.get(
        tg_id=update.effective_chat.id
    )
    profile.liked_stuff.add(random_photo[update.effective_chat.id][0])


def write_exchange_photo_to_db(update: Update):
    profile = Profile.objects.get(
        tg_id=update.effective_chat.id
    )
    profile.exchange_stuff.add(random_photo_ex[update.effective_chat.id][0])


def send_photo_to_user(update: Update, context, path):
    
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=path,
        reply_markup=main_keyboard(update.effective_chat.id)
    )


def get_liked_stuff(update: Update):
    liked_stuff = Profile.objects.filter(liked_stuff__isnull=False).filter(tg_id=update.effective_chat.id)
    print(liked_stuff)
    if liked_stuff:
        liked_stuff = [[j.photo for j in i.liked_stuff.all()] for i in liked_stuff.all()][0]
        return liked_stuff
    else:
        return []


def get_owner_photo(update):
    print(random_photo_ex)
    photo = random_photo_ex[update.effective_chat.id][-1]
    message = Message.objects.get(photo=photo)
    profile = message.profile
    print(profile.name)
    return profile


def get_to_exchange_users(profile):
    exchange_stuff = profile.exchange_stuff
    exchange_users = []
    if len(exchange_stuff.all()) > 0:
        print(exchange_stuff.all())
        messages = Message.objects.filter(photo__in=exchange_stuff.all())
        exchange_users = set([i.profile for i in messages])
        exchange_users1 = [i.name for i in exchange_users]
        exchange_users = [i.tg_id for i in exchange_users]
        print(exchange_users1)

        return exchange_users
    return exchange_users


def get_filled_messages(update: Update):
    exclude_profile = Profile.objects.get(tg_id=update.effective_chat.id)

    messages = Message.objects.exclude(profile=exclude_profile)

    messages = messages.exclude(category__isnull=True).exclude(category__exact='')
    messages = messages.exclude(name__isnull=True).exclude(name__exact='')
    return messages


def get_message_random_photo(update):
    messages = get_filled_messages(update)
    message = random.choice(messages)

    photo = message.photo
    photo = [p for p in photo.all()][0]
    return photo


def get_photo_to_show(update: Update):
    liked_stuff = get_liked_stuff(update)
    if liked_stuff:
        liked_photos = Photo.objects.filter(photo__in=liked_stuff)
        message_photos = [get_message_random_photo(update) for _ in range(25)]
        photos = list(liked_photos) + message_photos
        photo = random.choice(photos)
        print(photo)
        random_photo[update.effective_chat.id].clear()
        random_photo[update.effective_chat.id].append(photo)
        return photo.photo, photo

    else:
        photo = get_message_random_photo(update)

        random_photo[update.effective_chat.id].clear()
        random_photo[update.effective_chat.id].append(photo)
        return photo.photo, photo