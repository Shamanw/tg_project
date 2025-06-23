from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.bot_settings import *


async def deposit_choose_kb(callback_data_back = 'START'):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='💲 Перевод по USDT адресу',
                    callback_data=f'pay|m|usdt'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🤖 CryptoBot (USDT)',
                    callback_data=f'pay|m|cb'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='⬅️ Назад',
                    callback_data=callback_data_back
                ),
            ],
        ]
    )
    return markup

