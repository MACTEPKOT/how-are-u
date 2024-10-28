import sqlite3
import random
import telebot
from telebot import types

# Создаем и инициализируем базу данных
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER UNIQUE NOT NULL
)
""")
conn.commit()

# Инициализируем бота
API_TOKEN = '7977756376:AAEtbcAjF1iWVBIfJQD3GGjMU4U6VQNSN8c'
bot = telebot.TeleBot(API_TOKEN)

# Случайные ответы на вопрос "Как дела?"
responses = ["Все отлично!", "Неплохо, спасибо!", "Хорошо, как у тебя?", "Замечательно!", "Так себе..."]

# Функция для проверки регистрации пользователя
def is_user_registered(tg_id):
    cursor.execute("SELECT id FROM users WHERE tg_id = ?", (tg_id,))
    return cursor.fetchone() is not None

# Функция для регистрации пользователя
def register_user(tg_id):
    cursor.execute("INSERT OR IGNORE INTO users (tg_id) VALUES (?)", (tg_id,))
    conn.commit()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    # Проверяем, зарегистрирован ли пользователь
    if not is_user_registered(message.from_user.id):
        register_user(message.from_user.id)
        bot.send_message(message.chat.id, "Вы зарегистрированы!")
    else:
        bot.send_message(message.chat.id, "Вы уже зарегистрированы.")
    show_main_menu(message)

# Обработчик команды /status
@bot.message_handler(commands=['status'])
def status(message):
    if is_user_registered(message.from_user.id):
        bot.send_message(message.chat.id, "Вы зарегистрированы.")
    else:
        bot.send_message(message.chat.id, "Вы не зарегистрированы. Нажмите /start для регистрации.")

# Обработчик сообщения "Как дела?"
@bot.message_handler(func=lambda message: message.text.lower() == "как дела?")
def how_are_you(message):
    if is_user_registered(message.from_user.id):
        response = random.choice(responses)
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Сначала зарегистрируйтесь с помощью команды /start.")

# Кнопки для команд
def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    status_btn = types.KeyboardButton("Проверить статус")
    how_are_you_btn = types.KeyboardButton("Как дела?")
    markup.add(status_btn, how_are_you_btn)
    bot.send_message(message.chat.id, "Выберите команду:", reply_markup=markup)

# Обработчик для кнопки "Проверить статус"
@bot.message_handler(func=lambda message: message.text == "Проверить статус")
def handle_status_button(message):
    status(message)

# Обработчик для кнопки "Как дела?"
@bot.message_handler(func=lambda message: message.text == "Как дела?")
def handle_how_are_you_button(message):
    how_are_you(message)

# Запуск бота
bot.polling(none_stop=True)
