# - *- coding: utf- 8 - *-
from aiogram import types, Dispatcher
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message
from aiogram.utils.exceptions import Throttled

from stringsbot.data.config import get_admins


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit=0.5, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: Message, data: dict):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        if handler:
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
            key = getattr(handler, "throttling_key", f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        if message.from_user.id not in get_admins():
            try:
                await dispatcher.throttle(key, rate=limit)
            except Throttled as t:
                await self.message_throttled(message, t)
                raise CancelHandler()

    @staticmethod
    async def message_throttled(message: types.Message, throttled: Throttled):
        if throttled.exceeded_count <= 2:
            await message.reply("<b>❗ Пожалуйста, не спамьте.</b>")
