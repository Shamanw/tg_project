from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.users import *
from database.commands.groups import *
from database.commands.bot_settings import *


async def send_all_kb_menu_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f'👨‍💻 Рассылка по дропам',
                    callback_data='send|d|m'
                ),
            ],
            # [
            #     InlineKeyboardButton(
            #         text=f'🥷 Рассылка по клиентскому боту',
            #         callback_data='send|c|m'
            #     ),
            # ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='START'
                ),
            ],
        ]
    )
    return markup



