import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers import router
from db import init_db


async def main():
    logging.basicConfig(level=logging.INFO)

    # 🔹 создаём БД
    init_db()

    # 🔹 бот
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # 🔹 роутеры
    dp.include_router(router)

    # 🔹 команды
    await bot.set_my_commands([
        BotCommand(command="start", description="Запуск"),
        BotCommand(command="agpn", description="Меню"),
    ])

    print("✅ Бот запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())