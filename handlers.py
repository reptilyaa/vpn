from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

from vpn.wg_manager import generate_config
from keyboards import main_menu, info_menu

# если у тебя уже есть db.py (триал система)
from db import create_user, is_active

router = Router()

WELCOME_TEXT = """
👋 Добро пожаловать в AGPN

🔒 Современный ускоритель интернета
⚡ Быстрая выдача конфигов
🌍 Стабильное соединение

Используй меню ниже 👇
"""

INFO_TEXTS = {
    "info_console": """💻 Ускоритель интернета на консоль

🎮 Роутер с ускорением для PS5

❌ Раздача интернета с ускорением с телефона не работает

🚀 Решение — отдельный роутер с ускорением
📡 Keenetic или аналог
⚙️ Настройка через LAN
""",

    "info_server": """🖥 Свой сервер (VPS)

🌍 Твой личный VPN сервер

⚡ Плюсы:
• стабильность
• высокая скорость
• нет блокировок

☁️ VPS любой (TimeWeb и т.д.)
""",

    "info_whitelist": """🤍 Белые списки и Xray

🚀 Маскировка трафика

❌ Сервисы блокируют VPN
✔ Xray обходит блокировки

👉 интернет работает даже при ограничениях
"""
}


# ---------------- START ----------------
@router.message(Command("start"))
async def start(msg: types.Message):
    # создаём пользователя и триал 7 дней
    create_user(msg.from_user.id)

    await msg.answer(WELCOME_TEXT, reply_markup=main_menu())


# ---------------- MENU ----------------
@router.message(Command("agpn"))
async def agpn(msg: types.Message):
    await msg.answer("📱 Главное меню:", reply_markup=main_menu())


# ---------------- INFO ----------------
@router.callback_query(lambda c: c.data == "info")
async def info(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ Информация:",
        reply_markup=info_menu()
    )
    await callback.answer()


@router.callback_query(lambda c: c.data in ["info_console", "info_server", "info_whitelist"])
async def info_switch(callback: types.CallbackQuery):
    text = INFO_TEXTS.get(callback.data)

    if text:
        await callback.message.edit_text(text, reply_markup=info_menu())

    await callback.answer()


@router.callback_query(lambda c: c.data == "back_main")
async def back(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📱 Главное меню:",
        reply_markup=main_menu()
    )
    await callback.answer()


# ---------------- VPN GENERATION ----------------
@router.callback_query(F.data == "get_vpn")
async def get_vpn(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # 🔐 проверка триала
    if not is_active(user_id):
        await callback.message.answer("❌ Триал закончился или доступ закрыт")
        await callback.answer()
        return

    try:
        # 🔑 генерация VPN конфига
        config = generate_config(user_id)

        file = BufferedInputFile(
            config.encode(),
            filename="vpn.conf"
        )

        await callback.message.answer_document(
            document=file,
            caption="⚡ Ваш VPN конфиг готов"
        )

    except Exception as e:
        await callback.message.answer(f"❌ Ошибка генерации VPN:\n{e}")

    await callback.answer()