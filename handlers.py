from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

# ❗ ВАЖНО: убери vpn. если папки vpn нет
from wg_manager import generate_config, delete_peer
from keyboards import main_menu, info_menu, admin_menu
from db import (
    create_user,
    is_active,
    get_active_configs,
    deactivate_user,
    save_config,
    get_user_configs
)

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

        # ⚡ получаем конфиг
        config, public_key = generate_config(user_id)

        # 💾 сохраняем
        save_config(user_id, public_key, config)

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


# ---------------- DELETE VPN ----------------
@router.message(Command("delete_vpn"))
async def delete_vpn(msg: types.Message):
    user_id = msg.from_user.id

    configs = get_user_configs(user_id)

    if not configs:
        await msg.answer("❌ У тебя нет активных конфигов")
        return

    for (public_key,) in configs:
        try:
            delete_peer(public_key)
        except Exception as e:
            await msg.answer(f"❌ Ошибка удаления:\n{e}")
            return

    deactivate_user(user_id)

    await msg.answer("✅ Все VPN конфиги удалены")


# ---------------- SUPPORT ----------------
@router.callback_query(F.data == "support")
async def support(callback: types.CallbackQuery):
    await callback.message.answer(
        "🧑‍💻 Поддержка:\n\nПиши сюда: @your_support"
    )
    await callback.answer()


# ---------------- ADMIN PANEL ----------------
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


# ---------------- ADMIN USERS ----------------
@router.callback_query(F.data == "admin_users")
async def admin_users(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    users = get_active_configs()

    if not users:
        await callback.message.answer("❌ Нет активных пользователей")
        return

    text = "👥 Активные пользователи:\n\n"

    for user_id, created_at in users:
        text += f"ID: {user_id}\nВыдан: {created_at}\n\n"

    await callback.message.answer(text)
    await callback.answer()


# ---------------- ADMIN BAN ----------------
@router.message(Command("ban"))
async def ban_user(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    parts = msg.text.split()

    if len(parts) < 2:
        await msg.answer("Используй: /ban user_id")
        return

    try:
        user_id = int(parts[1])

        configs = get_user_configs(user_id)

        if not configs:
            await msg.answer("❌ У пользователя нет активных конфигов")
            return

        deleted = 0
        failed = 0

        for (public_key,) in configs:
            try:
                delete_peer(public_key)
                deleted += 1
            except Exception as e:
                failed += 1
                print(f"[BAN ERROR] {e}")

        # 🔥 ДЕАКТИВАЦИЯ ВСЕХ КОНФИГОВ
        deactivate_user(user_id)

        await msg.answer(
            f"⛔ Пользователь {user_id} отключён\n"
            f"Удалено конфигов: {deleted}\n"
            f"Ошибок удаления: {failed}"
        )

    except ValueError:
        await msg.answer("❌ user_id должен быть числом")