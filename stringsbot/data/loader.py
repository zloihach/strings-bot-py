from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from stringsbot.data.config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage = MemoryStorage())
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


