from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


show_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='ℹ️ Главное меню')
        ]
    ],
    resize_keyboard=True
)

