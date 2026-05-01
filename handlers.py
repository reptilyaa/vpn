from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

from vpn.wg_manager import generate_config
from keyboards import main_menu, info_menu
from keyboards import main_menu, info_menu, admin_menu
from db import create_user, is_active
ADMIN_ID = 1027906192

router = Router()

WELCOME_TEXT = """
👋 Добро пожаловать в AGPN

🔒 Современный VPN сервис
⚡ Быстрая выдача конфигов
🌍 Стабильное соединение

Используй меню ниже 👇
"""

INFO_TEXTS = {
    "info_console": "💻 Консоль / PS5 VPN инструкция",
    "info_server": "🖥 VPS сервер VPN",
    "info_whitelist": "🤍 Обход блокировок через Xray"
}


# ---------------- START ----------------
@router.message(Command("start"))
async def start(msg: types.Message):
    create_user(msg.from_user.id)

    await msg.answer(
        WELCOME_TEXT,
        reply_markup=main_menu()
    )


# ---------------- MENU ----------------
@router.message(Command("agpn"))
async def agpn(msg: types.Message):
    await msg.answer("📱 Главное меню:", reply_markup=main_menu())


# ---------------- INFO ----------------
@router.callback_query(F.data == "info")
async def info(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ Информация:",
        reply_markup=info_menu()
    )
    await callback.answer()


@router.callback_query(F.data.in_(["info_console", "info_server", "info_whitelist"]))
async def info_switch(callback: types.CallbackQuery):
    text = INFO_TEXTS.get(callback.data, "Нет данных")

    await callback.message.edit_text(
        text,
        reply_markup=info_menu()
    )

    await callback.answer()


@router.callback_query(F.data == "back_main")
async def back(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📱 Главное меню:",
        reply_markup=main_menu()
    )
    await callback.answer()


# ---------------- VPN ----------------
@router.callback_query(F.data == "get_vpn")
async def get_vpn(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    try:
        # 🔐 проверка триала
        if not is_active(user_id):
            await callback.message.answer("⛔ Ваш триал истёк")
            return

        # ⚡ получаем конфиг через VPS API
        config = generate_config(user_id)

        await callback.message.answer_document(
            BufferedInputFile(
                config.encode(),
                filename="vpn.conf"
            ),
            caption="⚡ Ваш VPN конфиг готов"
        )

    except Exception as e:
        await callback.message.answer(f"❌ Ошибка VPN:\n{e}")

    await callback.answer()

    @router.callback_query(F.data == "support")
    async def support(callback: types.CallbackQuery):
        await callback.message.answer(
            "🧑‍💻 Поддержка:\n\nПиши сюда: @your_support"
        )
        await callback.answer()

@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    await callback.message.edit_text(
        "🧠 Админ панель",
        reply_markup=admin_menu()
    )
    await callback.answer()