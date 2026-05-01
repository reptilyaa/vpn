from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import SUPPORT_URL, CHANNEL_URL, WEBAPP_URL


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚀 Купить",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ],
        [
            InlineKeyboardButton(text="⚡ Получить VPN", callback_data="get_vpn")
        ],
        [
            InlineKeyboardButton(text="🛠 Поддержка", url=SUPPORT_URL),
            InlineKeyboardButton(text="📢 Канал", url=CHANNEL_URL)
        ],
        [
            InlineKeyboardButton(text="ℹ️ Информация", callback_data="info")
        ],
        [
            InlineKeyboardButton(text="🧠 Админ панель", callback_data="admin_panel")
        ]
    ])


def info_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💻 Ускорение на консоль", callback_data="info_console")
        ],
        [
            InlineKeyboardButton(text="🖥 Свой сервер", callback_data="info_server")
        ],
        [
            InlineKeyboardButton(text="🤍 Белые списки", callback_data="info_whitelist")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")
        ]
    ])


# ---------------- ADMIN MENU ----------------

def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Пользователи", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton(text="⛔ Обновить список", callback_data="admin_panel")
        ],
        [
            InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back_main")
        ]
    ])