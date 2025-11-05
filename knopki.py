from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💳 Реквизиты"),
            KeyboardButton(text="📋 Продать группу")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False 
)


req_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔸 TON Кошелек")],
        [KeyboardButton(text="🇷🇺 Карты РФ")],
        [KeyboardButton(text="🇺🇦 Карты Украины")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

req_m_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Изменить реквизиты", callback_data="req_modify")],
    [InlineKeyboardButton(text="Назад", callback_data="req_back")]
])