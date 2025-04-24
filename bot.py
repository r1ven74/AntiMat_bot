import telebot
import logging
import time
import threading
import re
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    'block_mats': False,
    'block_links': False,
    'block_spam': False,
    'token': '-'
}


class BotConfig:
    def __init__(self):
        self.lock = threading.Lock()
        self.last_modified = 0
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()

    def load_config(self):
        try:
            current_modified = os.path.getmtime(CONFIG_FILE)
            if current_modified != self.last_modified:
                with self.lock:
                    with open(CONFIG_FILE, 'r') as f:
                        self.config = json.load(f)
                    self.last_modified = current_modified
        except (FileNotFoundError, json.JSONDecodeError):
            self.save_config()

    def save_config(self):
        with self.lock:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)

    def get(self, key):
        self.load_config()
        with self.lock:
            return self.config.get(key)

def update_json_file(file_path, key, new_value):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    if key in data:
        data[key] = new_value
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

config = BotConfig()
bot = telebot.TeleBot(config.get('token'))

user_messages = {}
user_blocks = {}
spam_lock = threading.Lock()
BLOCK_DURATION = 90

translit = {
    'c': 'с', 'y': 'у', 'x': 'х', 'e': 'е', 'p': 'р',
    'a': 'а', 'b': 'в', 'h': 'х', 'k': 'к', 'd': 'д',
    'f': 'ф', 'g': 'г', 'i': 'и', 'j': 'й', 'l': 'л',
    'm': 'м', 'n': 'н', 'o': 'о', 'q': 'к', 'r': 'р',
    's': 'с', 't': 'т', 'u': 'у', 'v': 'в', 'w': 'в', 'z': 'з'
}

mats = []
try:
    with open('mats.txt', 'r', encoding='utf-8') as f:
        mats = [line.strip().lower() for line in f]
except FileNotFoundError:
    logger.error("нету ффайла с матами")

URL_PATTERN = re.compile(
    r'(https?://\S+|www\.\S+|t\.me/\S+|@\w+)',
    re.IGNORECASE
)


def normalize(text):
    return ''.join([translit.get(c, c) for c in text.lower()])


def check_spam(user_id, text, message_id):
    with spam_lock:
        now = time.time()
        user_data = user_messages.get(user_id, [])
        user_data = [x for x in user_data if now - x[1] <= 60]
        normalized = normalize(text)

        user_data.append((normalized, now, message_id))
        user_messages[user_id] = user_data

        spam_count = sum(1 for x in user_data if x[0] == normalized)

        if spam_count >= 5:
            to_delete = [x[2] for x in user_data if x[0] == normalized]
            user_blocks[user_id] = {normalized: now + BLOCK_DURATION}
            return to_delete
        return None


@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if not message.text:
        return

    user_id = message.from_user.id
    text = message.text
    normalized = normalize(text)
    now = time.time()

    logger.info(
        f"Current settings: mats={config.get('block_mats')}, links={config.get('block_links')}, spam={config.get('block_spam')}")

    if user_id in user_blocks:
        for blocked_text, end_time in user_blocks[user_id].items():
            if blocked_text == normalized and now < end_time:
                try:
                    bot.delete_message(message.chat.id, message.message_id)
                    logger.info(f"заблокированное сообщение удалено: {text}")
                    return
                except Exception as e:
                    logger.error(f"ошибка удаления {e}")
                return

    if config.get('block_spam'):
        if spam_list := check_spam(user_id, text, message.message_id):
            for msg_id in spam_list:
                try:
                    bot.delete_message(message.chat.id, msg_id)
                    time.sleep(0.3)
                except Exception as e:
                    if "message to delete not found" not in str(e):
                        logger.error(f"ошибка удаления спама {e}")
            logger.info(f"удалено {len(spam_list)} спам сообщ")
            return

    if config.get('block_mats') and any(word in normalized for word in mats):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            logger.info(f"удалил плохое слово: {text}")
            return
        except Exception as e:
            logger.error(f"ошибка удаления мата {e}")

    if config.get('block_links') and URL_PATTERN.search(text):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            logger.info(f"удалил ссылку: {text}")
            return
        except Exception as e:
            logger.error(f"ошибка при удалении ссылки: {e}")


def run_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logger.error(f"ошибка бота: {e}")
            time.sleep(10)
