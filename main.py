import telebot
from Db import *
from config import *
from speech_kit import text_to_speech
from telebot.types import *
bot = telebot.TeleBot(telebot_token)
create_table()


def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard


def is_tts_symbol_limit(message, text):
    user_id = message.from_user.id
    text_symbols = len(text)

    # Функция из БД для подсчёта всех потраченных пользователем символов
    all_symbols = count_all_symbol(user_id) + text_symbols

    # Сравниваем all_symbols с количеством доступных пользователю символов
    if all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}. Использовано: {all_symbols} символов. Доступно: {MAX_USER_TTS_SYMBOLS - all_symbols}"
        bot.send_message(user_id, msg)
        return None

    # Сравниваем количество символов в тексте с максимальным количеством символов в тексте
    if text_symbols >= MAX_TTS_SYMBOLS:
        msg = f"Превышен лимит SpeechKit TTS на запрос {MAX_TTS_SYMBOLS}, в сообщении {text_symbols} символов"
        bot.send_message(user_id, msg)
        return None
    return len(text)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, 'Это TTS-бот для озвучки текста. Чтобы озвучить текст, напишите "/tts".', reply_markup=create_keyboard(["/help", '/tts']))


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, 'Это TTS-бот для озвучки текста. Чтобы озвучить текст, напишите "/tts" а следующим сообщением то/, что нужно озвучить. Автор: @MAPPPC. No rights reserved.', reply_markup=create_keyboard(["/help", '/tts']))


@bot.message_handler(commands=['tts'])
def tts_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь следующим сообщеним текст, чтобы я его озвучил!')
    bot.register_next_step_handler(message, tts)


def tts(message):
    user_id = message.from_user.id
    text = message.text

    # Проверка, что сообщение действительно текстовое
    if message.content_type != 'text':
        bot.send_message(user_id, 'Отправь текстовое сообщение')
        bot.register_next_step_handler(message, tts)
        return

        # Считаем символы в тексте и проверяем сумму потраченных символов
    text_symbol = is_tts_symbol_limit(message, text)
    if text_symbol is None:
        return

    # Записываем сообщение и кол-во символов в БД
    insert_row(user_id, text, text_symbol)

    # Получаем статус и содержимое ответа от SpeechKit
    status, content = text_to_speech(text)

    # Если статус True - отправляем голосовое сообщение, иначе - сообщение об ошибке
    if status:
        bot.send_voice(user_id, content)
    else:
        bot.send_message(user_id, content)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.send_message(message.from_user.id, f'Вы написали {message.text}. Чтобы озвучить текст, надо отправить команду /tts, а потом уже писать текст \nДля большей информации нажмите /help')

bot.polling()
