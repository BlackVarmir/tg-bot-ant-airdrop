import telebot
import sqlite3
from telebot import types
from background import keep_alive 

bot = telebot.TeleBot('6845331947:AAHJxcCZjKrn2lF3f7A5C2mnpgKn7cjVChc')

# Создайте базу данных и таблицу для хранения данных пользователя
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        subscribed_telegram_channel BOOLEAN,
        twitter_username TEXT,
        twitter_reposted BOOLEAN
    )
''')
conn.commit()
conn.close()

# Словарь для отслеживания состояния пользователя
user_state = {}

# Состояния регистрации
USERNAME, TELEGRAM_CHANNEL, TWITTER_SUBSCRIBE, TWITTER_REPOST = range(4)

# Обработка команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_state[user_id] = USERNAME
    bot.send_message(user_id, "Для начала регистрации введите ваш @username:")

# Обработка ввода @username
@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == USERNAME)
def handle_username(message):
    user_id = message.from_user.id
    username = message.text
    if "@" in username:
        user_state[user_id] = TELEGRAM_CHANNEL
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        conn.close()
        menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        menu_markup.row("Готово")
        message = f"Вы ввели username: {username}. Теперь подпишитесь на [Telegram](https://t.me/ant_airdrop_channel) канал и нажмите 'Готово'."
        bot.send_message(user_id, message, parse_mode="Markdown", reply_markup=menu_markup)

    else:
        bot.send_message(user_id, "Username должен содержать символ '@'. Попробуйте еще раз.")

# Обработка подписки на Telegram канал
@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == TELEGRAM_CHANNEL)
def handle_telegram_subscription(message):
    user_id = message.from_user.id
    text = message.text.lower()
    if text == "готово":
        user_state[user_id] = TWITTER_SUBSCRIBE
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET subscribed_telegram_channel = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        bot.send_message(user_id, "Вы подписались на Telegram канал. Теперь подпишитесь на Twitter и введите ваш Twitter username для проверки подписки.")
    else:
        bot.send_message(user_id, "Чтобы продолжить, подпишитесь на Telegram канал и напишите 'Готово'.")

# Обработка подписки на Twitter и репоста
@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == TWITTER_SUBSCRIBE)
def handle_twitter_subscription(message):
    user_id = message.from_user.id
    twitter_username = message.text
    # Здесь должна быть проверка подписки и репоста на Twitter, используя Twitter API
    # После успешной проверки:
    user_state[user_id] = TWITTER_REPOST
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET twitter_username = ? WHERE user_id = ?", (twitter_username, user_id))
    conn.commit()
    conn.close()
    bot.send_message(user_id, f"Вы подписались на Twitter. Теперь выполните репост и напишите 'Репост выполнен'.")

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == TWITTER_REPOST)
def handle_twitter_repost(message):
    user_id = message.from_user.id
    text = message.text.lower()
    if "репост выполнен" in text:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET twitter_reposted = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        bot.send_message(user_id, "Регистрация завершена. Все данные сохранены.")
        del user_state[user_id]
    else:
        bot.send_message(user_id, "Для завершения регистрации выполните репост и напишите 'Репост выполнен'.")

keep_alive()
# Запуск бота
bot.polling(non_stop=True, interval=0)
      