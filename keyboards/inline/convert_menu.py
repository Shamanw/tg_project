import asyncio

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.main import *

from utils.misc import decline_day, famount, get_time_at_period


async def convert_menu_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🗂 tdata > 🗄 .session (TL)',
                    callback_data=f'CONVERT|tdata_to_session_tl'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🗄 .session (TL) > 🗂 tdata',
                    callback_data=f'CONVERT|session_tl_to_tdata'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🗂 Проверка на валид: tdata',
                    callback_data=f'CONVERT|valid_tdata'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🗄 Проверка на валид: .session (TL)',
                    callback_data=f'CONVERT|valid_session'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'‹ Назад',
                    callback_data=f'START'
                ),
                InlineKeyboardButton(
                    text=f'Обновить',
                    callback_data=f'CONVERT|M'
                )
            ]
        ]
    )
    return markup

