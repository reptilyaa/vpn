from db import init_db
init_db()
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers import router


async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(router)

    # ✅ добавили команды в меню Telegram
    await bot.set_my_commands([
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="agpn", description="Открыть меню"),
    ])

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())