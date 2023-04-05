import sys

import aiogram
import csv
import os
import random
import datetime
import json

import colorama as colorama
from aiogram import Dispatcher
from aiogram.utils import executor

from stringsbot.utils.misc.bot_commands import set_commands
from stringsbot.utils.misc.bot_logging import bot_logger

from stringsbot.data.config import get_admins
from stringsbot.data.loader import dp, bot
from stringsbot.middlewares import setup_middlewares


# Функция для проверки, прошло ли 24 часа с момента последнего получения базы для данного пользователя
def check_time(user_id, data):
    for user in data['users']:
        if user['id'] == user_id:
            last_time = datetime.datetime.fromisoformat(user['last_time'])
            delta = datetime.datetime.now() - last_time
            return delta.days >= 1 or user.get('is_admin', False)
    return True


# Функция для проверки, есть ли пользователь в списке
def check_user(user_id, data):
    for user in data['users']:
        if user['id'] == user_id:
            return True, user
    return False, None


# Функция для сохранения информации о новом пользователе
def save_user(user_id, telegram_login, data):
    new_user = {
        'id': user_id,
        'telegram_login': telegram_login,
        'last_time': datetime.datetime.now().isoformat(),
        'count': 0,
        'is_admin': False
    }
    data['users'].append(new_user)


# Функция для сохранения времени последнего получения базы для данного пользователя
def save_time(user_id, data):
    for user in data['users']:
        if user['id'] == user_id:
            user['last_time'] = datetime.datetime.now().isoformat()
            user['count'] += 1
            break


# Функция для вывода статистики по всем пользователям
async def stats(message: aiogram.types.Message):
    if os.path.exists('data.json'):
        with open('data.json', 'r') as file:
            data = json.load(file)
        stats_text = ''
        for user in data['users']:
            stats_text += f"{user['telegram_login']}: {user.get('count', 0)} раз\n"
        stats_text += f"Всего пользователей: {len(data['users'])}"
        await message.answer(stats_text)
    else:
        await message.answer('Нет данных о пользователях.')


# Функция для вывода количества строк в файле links.txt
async def links(message: aiogram.types.Message):
    if os.path.exists('stringsbot/links.txt'):
        with open('stringsbot/links.txt', 'r') as file:
            links_count = len(file.readlines())
        await message.answer(f'Количество строк в файле links.txt: {links_count}')
    else:
        await message.answer('Файл links.txt не найден.')


# Функция для удаления строк из файла links.txt после их отправки пользователю
def delete_links(links_to_delete):
    if os.path.exists('stringsbot/links.txt'):
        with open('stringsbot/links.txt', 'r') as file:
            links = [line.strip() for line in file.readlines()]
        links_to_save = []
        for i, link in enumerate(links):
            if i + 1 not in links_to_delete:
                links_to_save.append(link)
        with open('stringsbot/links.txt', 'w') as file:
            file.write('\n'.join(links_to_save))


# Функция для отправки сообщения всем пользователям бота
async def send_to_all(message: aiogram.types.Message):
    user_id = message.from_user.id
    if os.path.exists('data.json'):
        with open('data.json', 'r') as file:
            data = json.load(file)
        user_exists, user_data = check_user(user_id, data)
        if user_data and user_data['is_admin']:
            await message.answer('Введите текст сообщения для рассылки:')
            dp.register_message_handler(send_text_to_all)
        else:
            await message.answer('Вы не являетесь администратором.')
    else:
        await message.answer('Нет данных о пользователях.')


# Функция для отправки сообщения всем пользователям бота (часть 2)
async def send_text_to_all(message: aiogram.types.Message):
    text = message.text
    with open('data.json', 'r') as file:
        data = json.load(file)
    for user in data['users']:
        try:
            await bot.send_message(user['id'], text)
        except Exception as e:
            print(f"Ошибка отправки сообщения пользователю {user['telegram_login']}: {str(e)}")
    dp.message_handlers.unregister(send_text_to_all)
    await message.answer(f'Сообщение "{text}" отправлено всем пользователям')


async def start(message: aiogram.types.Message):
    keyboard = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(aiogram.types.KeyboardButton('Получить базу'))
    user_id = message.from_user.id
    if os.path.exists('data.json'):
        with open('data.json', 'r') as file:
            data = json.load(file)
    else:
        data = {'users': []}
    user_exists, user_data = check_user(user_id, data)
    if not user_exists:
        save_user(user_id, message.from_user.username, data)
    if user_data and user_data['is_admin']:
        keyboard.add(
            aiogram.types.KeyboardButton('Статистика'),
            aiogram.types.KeyboardButton('Количество ссылок'),
            aiogram.types.KeyboardButton('Рассылка')
        )
    await message.answer('Привет! Нажми кнопку, чтобы получить базу.', reply_markup=keyboard)


async def get_links(message: aiogram.types.Message):
    if not os.path.exists('send'):
        os.makedirs('send')
    user_id = message.from_user.id
    if os.path.exists('data.json'):
        with open('data.json', 'r') as file:
            data = json.load(file)
    else:
        data = {'users': []}
    if check_time(user_id, data):
        with open('stringsbot/links.txt', 'r') as file:
            links = [line.strip() for line in file.readlines()[:50]]
        if links:
            filename = f'{random.getrandbits(32)}.csv'
            with open(f'send/{filename}', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows([[link] for link in links])
            with open(f'send/{filename}', 'rb') as file:
                await message.answer_document(file, disable_notification=True)
            user_exists, user_data = check_user(user_id, data)
            if not user_exists:
                save_user(user_id, message.from_user.username, data)
            save_time(user_id, data)
            with open('data.json', 'w') as file:
                json.dump(data, file)
            if not user_data:
                await message.answer('Вы получили базу')
            delete_links(list(range(1, len(links) + 1)))
        else:
            await message.answer('База пуста')
    else:
        await message.answer('Вы уже получили базу менее 24 часов назад.')


dp.register_message_handler(start, commands=['start'])
dp.register_message_handler(get_links, lambda message: message.text == 'Получить базу')
dp.register_message_handler(stats, lambda message: message.text == 'Статистика')
dp.register_message_handler(links, lambda message: message.text == 'Количество ссылок')
dp.register_message_handler(send_to_all, lambda message: message.text == 'Рассылка')


async def on_startup(dp: Dispatcher):
    await set_commands(dp)
    await dp.bot.delete_webhook()
    await dp.bot.get_updates(offset=-1)

    bot_logger.warning("BOT WAS STARTED")
    print(colorama.Fore.LIGHTYELLOW_EX + f"~~~~~ Bot was started - @{(await dp.bot.get_me()).username} ~~~~~")
    print(colorama.Fore.LIGHTBLUE_EX + "~~~~~ TG developer - @ferd_q & @muertome ~~~~~")
    print(colorama.Fore.RESET)

    if len(get_admins()) == 0: print("***** ENTER ADMIN ID IN settings.ini *****")


# Выполнение функции после выключения бота
async def on_shutdown(dp: Dispatcher):
    await dp.storage.close()
    await dp.storage.wait_closed()
    await (await dp.bot.get_session()).close()

    if sys.platform.startswith("win"):
        os.system("cls")
    else:
        os.system("clear")


if __name__ == '__main__':
    setup_middlewares(dp)
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
