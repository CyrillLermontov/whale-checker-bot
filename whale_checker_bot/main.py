from aiogram.utils import executor
from create_bot import dp
from handlers import client
from data import sqlite_db


async def on_startup(_):
    print('Bot online')
    sqlite_db.sql_start()



if __name__ == '__main__':
    client.register_handlers_client(dp)
    executor.start_polling(dp, skip_updates=True, on_startup = on_startup)

