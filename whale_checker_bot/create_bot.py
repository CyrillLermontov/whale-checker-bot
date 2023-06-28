from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import *


TOKEN = settings_json['telegram_token']


storage = MemoryStorage()


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)