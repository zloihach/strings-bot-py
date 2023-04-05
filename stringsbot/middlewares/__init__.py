# - *- coding: utf- 8 - *-
from aiogram import Dispatcher

#from stringsbot.middlewares.exists_user import ExistsUserMiddleware
from stringsbot.middlewares.throtling import ThrottlingMiddleware


# Подключение милдварей
def setup_middlewares(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())
