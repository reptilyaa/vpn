import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers import router
from db import init_db, get_expired_configs
from wg_manager import delete_peer


# ---------------- AUTO CLEAN ----------------
async def deactivate_expired():
    while True:
        expired = get_expired_configs()

        for public_key in expired:
            try:
                delete_peer(public_key)
                print(f"❌ Удалён просроченный конфиг: {public_key}")
            except Exception as e:
                print(f"Ошибка удаления: {e}")

        await asyncio.sleep(60)


# ---------------- MAIN ----------------
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

    # 🔥 запускаем авто-очистку
    asyncio.create_task(deactivate_expired())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())