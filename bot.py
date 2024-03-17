import telebot
import sqlite3
import random
from telebot import types

# Подключение к базе данных
conn = sqlite3.connect('base.db', check_same_thread=False)
cursor = conn.cursor()

# Создание объекта бота с указанием токена
bot = telebot.TeleBot("YOUR_BOT_TOKEN")

# Обработчик команды /start
@bot.message_handler(commands=['start'])

# Отправка приветственного сообщения
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот-помощник QA, с помощью меня вы сможете узнать среднестатистическую вероятность вопросов, как и сами ответы на вопросы, которые вероятно возникнут на собеседовании по специальности QA. \n\nДля получения ответа на вопрос, отправьте сообщение: \n/id 'Номер вопроса'")
    # Добавляем кнопки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Как пользоваться")
    item2 = types.KeyboardButton("Список вопросов")
    item3 = types.KeyboardButton("Случайный вопрос/ответ")
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


# Обработчик кнопки "Как пользоваться"
@bot.message_handler(func=lambda message: message.text == "Как пользоваться")
def how_to_use(message):
    bot.reply_to(message, "Для выбора вопроса введите команду /id и номер вопроса")

# Обработчик кнопки "Список вопросов"
@bot.message_handler(func=lambda message: message.text == "Список вопросов")
def list_questions(message):
    send_questions(message)

# Обработчик кнопки "Случайный вопрос/ответ"
@bot.message_handler(func=lambda message: message.text == "Случайный вопрос/ответ")
def random_question(message):
    send_random_question(message)

# Обработчик команды /question
@bot.message_handler(commands=['question'])
def send_questions(message):
    cursor.execute("SELECT id, question FROM qa")
    questions = cursor.fetchall()
    response = "\n".join([f"{row[0]} {row[1]}" for row in questions])
    bot.reply_to(message, response)

# Обработчик команды /random
@bot.message_handler(commands=['random'])
def send_random_question(message):
    cursor.execute("SELECT question, answer FROM qa ORDER BY RANDOM() LIMIT 1")
    random_qa = cursor.fetchone()
    response = f"Вопрос: {random_qa[0]}\n\nОтвет: <span class=\"tg-spoiler\">{random_qa[1]}</span>"
    bot.reply_to(message, response, parse_mode="HTML")


# Обработчик команды /id
@bot.message_handler(commands=['id'])
def send_question_by_id(message):
    try:
        id_number = int(message.text.split()[1])
        cursor.execute("SELECT question, answer FROM qa WHERE id = ?", (id_number,))
        qa = cursor.fetchone()
        if qa:
            response = f"Вопрос: {qa[0]}\n\nОтвет: {qa[1]}"
        else:
            response = "Вопрос с таким ID не найден."
        bot.reply_to(message, response)
    except IndexError:
        bot.reply_to(message, "Вы не указали ID.")
    except ValueError:
        bot.reply_to(message, "ID должен быть числом.")

# Обработчик неизвестных команд
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Я не понимаю эту команду. Воспользуйтесь кнопкой 'Как пользоваться' для получения списка команд.")

# Запуск бота
bot.polling()


