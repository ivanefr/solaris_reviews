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
    text = """Здравствуйте! 🌟

Благодарим вас за выбор программы от Соляриса! Нам важно ваше мнение, и мы хотели бы услышать ваш отзыв.

Обратная связь поможет нам улучшить качество обучения и сделать курсы еще лучше. 

Пожалуйста, уделите несколько минут, чтобы ответить на несколько вопросов и поделиться своими впечатлениями!"""
    bot.send_message(message.from_user.id, text, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "start")
def callback_worker(call):
    message = call.message
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Введите ваше ФИО.")
    bot.register_next_step_handler(message, get_name)


def get_name(message):
    data[message.chat.id] = {}
    data[message.chat.id]["name"] = message.text
    bot.send_message(chat_id=message.chat.id, text="В каком классе вы обучаетесь?")
    bot.register_next_step_handler(message, get_class)


def get_class(message):
    data[message.chat.id]["class"] = message.text
    bot.send_message(chat_id=message.chat.id, text="Введите ваш возраст.", )
    bot.register_next_step_handler(message, get_age)


def get_courses():
    with open('courses.txt', encoding='utf8') as f:
        courses = f.read().strip().split('\n')
    return courses


def get_age(message):
    data[message.chat.id]["age"] = message.text
    text = "Напишите название курса/интенсива/смены который вы прошли:"
    bot.send_message(chat_id=message.chat.id, text=text)
    bot.register_next_step_handler(message, get_course)


def get_course(message):
    data[message.chat.id]["course"] = message.text
    keyboard = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(text="Да", callback_data="q1_yes")
    keyboard.add(yes)
    no = types.InlineKeyboardButton(text="Нет", callback_data="q1_no")
    keyboard.add(no)

    bot.send_message(chat_id=message.chat.id,
                     text="Проживали ли вы в общежитие во время проведения курса?",
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("q1"))
def callback_q1(call):
    message = call.message
    if call.data == "q1_yes":
        data[message.chat.id]["Проживали ли вы в общежитие во время проведения курса?"] = "Да"
        keyboard = types.InlineKeyboardMarkup()
        yes = types.InlineKeyboardButton(text="Да", callback_data="q2_yes")
        keyboard.add(yes)
        no = types.InlineKeyboardButton(text="Нет", callback_data="q2_no")
        keyboard.add(no)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text="Устраивали ли вас условия проживания?", reply_markup=keyboard)
    else:
        data[message.chat.id]["Проживали ли вы в общежитие во время проведения курса?"] = "Нет"
        ask_q3(message)


def ask_q3(message, edit=True):
    keyboard = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(text="Да", callback_data="q3_yes")
    keyboard.add(yes)
    no = types.InlineKeyboardButton(text="Нет", callback_data="q3_no")
    keyboard.add(no)
    if not edit:
        bot.send_message(chat_id=message.chat.id, text="Были ли вам полезны лекции?",
                         reply_markup=keyboard)
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text="Были ли вам полезны лекции?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("q2"))
def callback_q2(call):
    message = call.message
    if call.data == "q2_yes":
        data[message.chat.id]["Устраивали ли вас условия проживания?"] = "Да"
        ask_q3(message)
    else:
        data[message.chat.id]["Устраивали ли вас условия проживания?"] = "Нет"
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text="Напишите конкретно что именно вам не понравилось")
        bot.register_next_step_handler(message, get_dop_info)


def get_dop_info(message):
    data[message.chat.id]["Напишите конкретно что именно вам не понравилось"] = message.text
    ask_q3(message, edit=False)


@bot.callback_query_handler(func=lambda call: call.data.startswith("q3"))
def callback_q3(call):
    message = call.message
    if call.data == "q3_yes":
        data[message.chat.id]["Были ли вам полезны лекции?"] = "Да"
    else:
        data[message.chat.id]["Были ли вам полезны лекции?"] = "Нет"
    keyboard = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(text="Да", callback_data="q4_yes")
    keyboard.add(yes)
    no = types.InlineKeyboardButton(text="Нет", callback_data="q4_no")
    keyboard.add(no)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text="Стали бы вы рекомендовать наши курсы друзьям/знакомым?",
                          reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("q4"))
def callback_q4(call):
    message = call.message
    if call.data == "q4_yes":
        data[message.chat.id]["Стали бы вы рекомендовать наши курсы друзьям/знакомым?"] = "Да"
    else:
        data[message.chat.id]["Стали бы вы рекомендовать наши курсы друзьям/знакомым?"] = "Нет"
    keyboard = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(text="Да", callback_data="q5_yes")
    keyboard.add(yes)
    no = types.InlineKeyboardButton(text="Нет", callback_data="q5_no")
    keyboard.add(no)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text="Посетили бы вы другие курсы/смены/интенсивы в Солярисе еще раз?",
                          reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("q5"))
def callback_q5(call):
    message = call.message
    if call.data == "q4_yes":
        data[message.chat.id]["Посетили бы вы другие курсы/смены/интенсивы в Солярисе еще раз?"] = "Да"
    else:
        data[message.chat.id]["Посетили бы вы другие курсы/смены/интенсивы в Солярисе еще раз?"] = "Нет"
    text = """Развернутый отзыв. 🌠

Напишите про ваши впечатления от курса/смены/интенсива. Расскажите, что вам понравилось, а что бы вы улучшили или изменили."""
    bot.edit_message_text(chat_id=message.chat.id, text=text, message_id=message.message_id)
    bot.register_next_step_handler(message, get_info)


def get_info(message):
    data[message.chat.id]["Развёрнутый отзыв"] = message.text
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    for i in range(1, 6):
        button = types.InlineKeyboardButton(text=str(i), callback_data=f"q7_{i}")
        buttons.append(button)
    keyboard.row(*buttons)
    bot.send_message(chat_id=message.chat.id, text="Оцените в целом мероприятие от 1 до 5",
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("q7"))
def callback_q3(call):
    message = call.message
    data[message.chat.id]["q3"] = int(call.data[-1])
    text = """Спасибо за ваш отзыв! 💫

Мы ценим ваше мнение и время, которое вы потратили на опрос. Обратная связь очень важна для улучшения нашей работы. 

Желаем вам удачи в учебе и надеемся увидеть вас снова!"""
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text=text)


bot.polling(none_stop=True, interval=0)
