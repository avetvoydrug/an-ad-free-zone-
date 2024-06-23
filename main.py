import os
import asyncio
from menu.database.models import async_main

from aiogram import Bot, Dispatcher
from menu.handlers import router
from menu.middlewares import AntiSpamMiddleware
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

async def main():
    await async_main()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Alles good!')
    