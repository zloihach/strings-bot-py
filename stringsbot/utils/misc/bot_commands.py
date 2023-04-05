# - *- coding: utf- 8 - *-
from aiogram import Dispatcher
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from stringsbot.data.config import get_admins



# dp.register_message_handler(start, commands=['start'])
# dp.register_message_handler(get_links, lambda message: message.text == 'Получить базу')
# dp.register_message_handler(stats, lambda message: message.text == 'Статистика')
# dp.register_message_handler(links, lambda message: message.text == 'Количество ссылок')
# dp.register_message_handler(send_to_all, lambda message: message.text == 'Рассылка')

# Команды для юзеров
user_commands = [
    BotCommand("start", "♻ Перезапустить бота"),
    BotCommand("get_strings", "📖 Получить базу"),
    BotCommand("support", "☎ Поддержка"),
    BotCommand("faq", "ℹ FAQ"),
]

# Команды для админов
admin_commands = [
    BotCommand("start", "♻ Перезапустить бота"),
    BotCommand("support", "☎ Поддержка"),
    BotCommand("faq", "ℹ FAQ"),
    BotCommand("db", "📦 Получить Базу Данных"),
    BotCommand("log", "🖨 Получить логи"),
]


# Установка команд
async def set_commands(dp: Dispatcher):
    await dp.bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    for admin in get_admins():
        try:
            await dp.bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin))
        except:
            pass
