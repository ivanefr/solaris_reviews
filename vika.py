import Config
import telebot
from telebot import types
from pymongo import MongoClient
from requests import get

# Настройка бд
client = MongoClient('mongodb://localhost:27017/')
db = client['RatingSolaris']

# настройка бота
bot = telebot.TeleBot(Config.TOKEN)


# Старт
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Оценить")
    item2 = types.KeyboardButton("/start")
    markup.add(item1, item2)

    bot.send_photo(message.chat.id,
                   get("https://optim.tildacdn.com/tild3265-3765-4261-b965-366538643031/-/format/webp/shapka_na_sayt.png").content)

    bot.send_message(message.chat.id,
                     "Добро пожаловать в бота для оценки центра <b>Солярис</b>, {0.first_name}".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def lala(message):
    if message.chat.type == 'private':

        if message.text == "Оценить":
            sent = bot.send_message(message.from_user.id, "Введите ФИО")
            bot.register_next_step_handler(sent, get_name)


def get_name(message):
    ratings_collection = db["Ratings"]
    user_id = message.from_user.id
    username = message.from_user.username
    name = message.text
    doc = {
        'user_id': user_id,
        'username': username,
        'name': name,
        'age': 0,
        'direction': 0,
        'q1': 0,
        'q2': 0

    }
    ratings_collection.insert_one(doc)
    sent = bot.send_message(message.from_user.id, "Введите возраст")
    bot.register_next_step_handler(sent, age)


def age(message):
    ratings_collection = db["Ratings"]
    user_id = message.from_user.id

    age = message.text

    ratings_collection.update_one({'user_id': user_id}, {'$set': {'age': age}})
    sent = bot.send_message(message.from_user.id, 'Введите направление')
    bot.register_next_step_handler(sent, derection)


def derection(message):
    ratings_collection = db["Ratings"]
    user_id = message.from_user.id
    derection = message.text

    ratings_collection.update_one({'user_id': user_id}, {'$set': {'direction': derection}})

    sent = bot.send_message(message.from_user.id, 'Отлично!Проверьте ваши данные')

    data = ratings_collection.find_one({'user_id': user_id}, {})
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Перейти к вопросам', callback_data='Questions')
    button2 = types.InlineKeyboardButton('Неправильные данные', callback_data='FalseDate')
    keyboard.add(button1, button2)
    bot.send_message(message.chat.id,
                     f"<b>🆔Username:</b>{data['username']}\n<b>ФИО:</b>{data['name']}\n<b>Возраст:</b>{data['age']}\n<b>Направление:</b>{data['direction']}",
                     reply_markup=keyboard, parse_mode="html")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'FalseDate':
                bot.send_message(call.message.chat.id, 'Попробуйте заполнить еще раз, нажав <b>Оценить</b>',
                                 parse_mode="html")
    except Exception as e:
        print(repr(e))


bot.polling(none_stop=True)
