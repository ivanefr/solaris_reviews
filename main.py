import os
import telebot
from telebot import types

token = os.environ.get("SOLARIS_TOKEN")
bot = telebot.TeleBot(token)

data = {}


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()
    key_start = types.InlineKeyboardButton(text="Начать", callback_data="start")
    keyboard.add(key_start)
    bot.send_message(message.from_user.id, "Привет!\nлалалалал", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "start")
def callback_worker(call):
    message = call.message
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Пришлите ФИО")
    bot.register_next_step_handler(message, get_name)


def get_name(message):
    data[message.chat.id] = {}
    data[message.chat.id]["name"] = message.text
    bot.send_message(chat_id=message.chat.id, text="Введите ваш возвраст")
    bot.register_next_step_handler(message, get_age)


def get_courses():
    with open('courses.txt', encoding='utf8') as f:
        courses = f.read().strip().split('\n')
    return courses


def get_age(message):
    data[message.chat.id]["age"] = message.text
    keyboard = types.InlineKeyboardMarkup()
    courses = get_courses()
    for num, course in enumerate(courses, start=1):
        button = types.InlineKeyboardButton(text=course, callback_data=f"course{num}")
        keyboard.add(button)
    text = "Выберите курс который вы прошли:"
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("course"))
def callback_course(call):
    message = call.message
    data[message.chat.id]["course"] = message.text
    keyboard = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(text="Да", callback_data="q1_yes")
    keyboard.add(yes)
    no = types.InlineKeyboardButton(text="Нет", callback_data="q1_no")
    keyboard.add(no)

    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text="понравилось?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("q1"))
def callback_q1(call):
    message = call.message
    if call.data == "q1_yes":
        data[message.chat.id]["like"] = True
    else:
        data[message.chat.id]["like"] = False
    keyboard = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(text="Да", callback_data="q2_yes")
    keyboard.add(yes)
    no = types.InlineKeyboardButton(text="Нет", callback_data="q2_no")
    keyboard.add(no)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text="рандомный вопрос??", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("q2"))
def callback_q2(call):
    message = call.message
    if call.data == "q1_yes":
        data[message.chat.id]["q2"] = True
    else:
        data[message.chat.id]["q1"] = False
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text="Напишите общее впечатление о смене/интенсиве")
    bot.register_next_step_handler(message, get_info)
    # bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
    #                       text="Отзыв получен, чтобы отправить повторный напишите /start")


def get_info(message):
    data[message.chat.id]["info"] = message.text
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    for i in range(1, 6):
        button = types.InlineKeyboardButton(text=str(i), callback_data=f"q3_{i}")
        buttons.append(button)
    keyboard.row(*buttons)
    bot.send_message(chat_id=message.chat.id, text="Оцените в целом мероприятие от 1 до 5",
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("q3"))
def callback_q3(call):
    message = call.message
    data[message.chat.id]["q3"] = int(call.data[-1])
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text="Вам отзыв принят, чтобы оставить еще один нажмите /start")

bot.polling(none_stop=True, interval=0)
