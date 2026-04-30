from aiogram import Router, types
from aiogram.filters import Command

from keyboards import main_menu, info_menu

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

Сегодня ускорение интернета — это уже не опция, а необходимость.  
Если на телефоне или ПК всё подключается за пару кликов, то с консолями всё гораздо сложнее.

❌ Раздача интернета с ускорением с телефона не работает — консоль всё равно подключается без него.

Из-за этого появляются проблемы:
• ошибки в играх (RDR2, MK11, Fortnite, BF)  
• недоступность серверов  
• блокировки от провайдеров  

🚀 Решение — отдельный роутер с ускорением

📡 Подойдёт роутер с поддержкой ускорения (например Keenetic)

⚙️ Как настроить:
1. Подключить роутер по LAN к основному  
2. Подключиться к его Wi-Fi  
3. Установить драйвера  
4. Дать доступ к сети  

🔐 После этого остаётся только настроить ускорение и подключить консоль
""",

    "info_server": """🖥 Свой сервер (VPS)

🌍 Что это?
Это твой личный ускоритель интернета, к которому можно подключить:
• телефон  
• ПК  
• консоль (PS5)  
• друзей и семью  

⚡ Почему это лучше:
• стабильность  
• высокая скорость  
• нет блокировок как у бесплатных ускорителей 

☁️ Где взять:
Можно использовать любой сервис VPS

🔥 Рекомендуется:
TimeWeb — стабильная работа и хорошая поддержка

⚙️ Настройка:
Создаёшь сервер → ставишь ускорение → получаешь конфиг → используешь

💡 После настройки у тебя будет полностью свой ускоритель
""",

    "info_whitelist": """🤍 Белые списки и Xray

⚠️ Проблема:
Некоторые сервисы определяют ускорение и блокируют доступ

🚀 Решение — Xray

Он маскирует трафик так, что сервисы не видят ускорение

---

📋 Белые списки

Когда включаются ограничения:
❌ не работают даже обычные приложения  
❌ доступ только к “разрешённым” сервисам  

💡 Как работает обход:
Твой трафик маскируется под разрешённые сервисы  
(например: VK, Яндекс и др.)

👉 В итоге интернет работает даже при ограничениях

---

🔧 Что использовать:
Клиенты с поддержкой Xray

💡 Для обхода белых списков лучше использовать специальные клиенты
"""
}


# /start
@router.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(WELCOME_TEXT, reply_markup=main_menu())


# /agpn
@router.message(Command("agpn"))
async def agpn(msg: types.Message):
    await msg.answer("📱 Главное меню:", reply_markup=main_menu())


# открыть инфо
@router.callback_query(lambda c: c.data == "info")
async def info(callback: types.CallbackQuery):
    await callback.message.edit_text("ℹ️ Информация:", reply_markup=info_menu())
    await callback.answer()


# переключение инфо (✅ FIX ошибки)
@router.callback_query(lambda c: c.data in ["info_console", "info_server", "info_whitelist"])
async def info_switch(callback: types.CallbackQuery):
    text = INFO_TEXTS.get(callback.data)

    # 👉 проверка чтобы не было ошибки
    if callback.message.text != text:
        await callback.message.edit_text(text, reply_markup=info_menu())

    await callback.answer()


# назад
@router.callback_query(lambda c: c.data == "back_main")
async def back(callback: types.CallbackQuery):
    await callback.message.edit_text("📱 Главное меню:", reply_markup=main_menu())
    await callback.answer()