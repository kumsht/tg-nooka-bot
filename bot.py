import sqlite3
import os
import requests
from datetime import datetime
from telegram.ext import Updater, MessageHandler, Filters

# Токен вашего бота Telegram
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Файл базы данных SQLite
DATABASE_FILE = 'notion_data.db'

# Функция для создания таблицы базы данных
def create_table():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notion_data
                 (id INTEGER PRIMARY KEY, api_key TEXT, database_id TEXT)''')
    conn.commit()
    conn.close()

# Функция для чтения данных из базы данных
def read_notion_data():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''SELECT * FROM notion_data''')
    data = c.fetchone()
    conn.close()
    return data

# Функция для записи данных в базу данных
def write_notion_data(api_key, database_id):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''INSERT INTO notion_data (api_key, database_id) VALUES (?, ?)''', (api_key, database_id))
    conn.commit()
    conn.close()

# Функция для проверки количества отправленных сообщений
def check_message_limit(user_id):
    global MONTH
    current_month = datetime.now().month
    if current_month != MONTH:
        MONTH = current_month
        messages_sent.clear()
    messages_sent.setdefault(user_id, 0)
    return messages_sent[user_id] >= 30

# Функция-обработчик для текстовых сообщений
def text_message_handler(update, context):
    user_id = update.message.from_user.id
    if not check_message_limit(user_id):
        text = update.message.text
        if send_text_to_notion(text):
            update.message.reply_text('Сообщение успешно отправлено в Notion!')
            messages_sent[user_id] += 1
        else:
            update.message.reply_text('Ошибка при отправке сообщения в Notion.')
    else:
        update.message.reply_text('Превышен лимит на количество сообщений за месяц. '
                                  'Пожалуйста, оформите подписку.')

# Функция-обработчик для изображений
def photo_message_handler(update, context):
    user_id = update.message.from_user.id
    if not check_message_limit(user_id):
        photo_file = update.message.photo[-1].get_file()
        photo_url = photo_file.file_path
        if send_photo_to_notion(photo_url):
            update.message.reply_text('Фото успешно отправлено в Notion!')
            messages_sent[user_id] += 1
        else:
            update.message.reply_text('Ошибка при отправке фото в Notion.')
    else:
        update.message.reply_text('Превышен лимит на количество сообщений за месяц. '
                                  'Пожалуйста, оформите подписку.')

def main():
    create_table()
    data = read_notion_data()
    if data:
        notion_token, database_id = data
    else:
        print("Введите данные Notion API:")
        notion_token = input("Notion API Key: ")
        database_id = input("Notion Database ID: ")
        write_notion_data(notion_token, database_id)

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_message_handler))
    dp.add_handler(MessageHandler(Filters.photo, photo_message_handler))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
