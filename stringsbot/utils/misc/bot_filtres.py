# - *- coding: utf- 8 - *-
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from stringsbot.data.config import get_admins
# from stringsbot.services.api_sqlite import get_settingsx


# Проверка на диалог в ЛС бота
class IsPrivate(BoundFilter):
    async def check(self, message):
        if "id" in message:
            return message.message.chat.type == types.ChatType.PRIVATE
        else:
            return message.chat.type == types.ChatType.PRIVATE


# Проверка на админа
class IsAdmin(BoundFilter):
    async def check(self, message: types.Message):
        if message.from_user.id in get_admins():
            return True
        else:
            return False
