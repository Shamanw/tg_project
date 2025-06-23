from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.converter_proxy_socks_5 import *


async def proxy_menu_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='➕ HTTP',
                    callback_data='CONVPROXY|ADD|HTTP|M'
                ),
                InlineKeyboardButton(
                    text='➕ SOCKS5',
                    callback_data='CONVPROXY|ADD|SOCKS5|M'
                )
            ],
            [
                InlineKeyboardButton(
                    text='📁 HTTP',
                    callback_data='CONVPROXY|TXT|HTTP|M'
                ),
                InlineKeyboardButton(
                    text='📁 SOCKS5',
                    callback_data='CONVPROXY|TXT|SOCKS5|M'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'🚫 [{len(await select_converter_proxy_socks_5s())}] Удаление',
                    callback_data='CONVPROXY|DELETE|M|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔄',
                    callback_data='CONVPROXY|M'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='START'
                )
            ]
        ]
    )
    return markup

async def add_menu_kb(scheme):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='1️⃣ username:password@hostname:port',
                    callback_data=f'CONVPROXY|ADD|{scheme}|T|0'
                )
            ],
            [
                InlineKeyboardButton(
                    text='2️⃣ username:password:hostname:port',
                    callback_data=f'CONVPROXY|ADD|{scheme}|T|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='3️⃣ hostname:port@username:password',
                    callback_data=f'CONVPROXY|ADD|{scheme}|T|2'
                )
            ],
            [
                InlineKeyboardButton(
                    text='4️⃣ hostname:port:username:password',
                    callback_data=f'CONVPROXY|ADD|{scheme}|T|3'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='CONVPROXY|M'
                )
            ]
        ]
    )
    return markup

async def txt_menu_kb(scheme):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='1️⃣ username:password@hostname:port',
                    callback_data=f'CONVPROXY|TXT|{scheme}|T|0'
                )
            ],
            [
                InlineKeyboardButton(
                    text='2️⃣ username:password:hostname:port',
                    callback_data=f'CONVPROXY|TXT|{scheme}|T|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='3️⃣ hostname:port@username:password',
                    callback_data=f'CONVPROXY|TXT|{scheme}|T|2'
                )
            ],
            [
                InlineKeyboardButton(
                    text='4️⃣ hostname:port:username:password',
                    callback_data=f'CONVPROXY|TXT|{scheme}|T|3'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='CONVPROXY|M'
                )
            ]
        ]
    )
    return markup


async def delete_proxy_kb(page):
    page_action = f'CONVPROXY|DELETE|M'
    writes = await select_converter_proxy_socks_5s()
    items_per_page = 30
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    for write in current_writes:
        buttons.append([
            InlineKeyboardButton(
                text=f'🚫 {write.scheme.upper()} {write.ip}:{write.port}@{write.login}:{write.password}',
                callback_data=f'CONVPROXY|DELETE|D|{page}'
            ),]
        )
    manage_buttons = []
    if page > 2:
        manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{page_action}|1'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    if start > 0: 
        manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{page_action}|{page - 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{page_action}|{page}'))
    if end < len(writes):
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{page_action}|{page + 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    if page < total_pages and page + 1 != total_pages:
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{page_action}|{total_pages}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    buttons.append(manage_buttons)
    buttons.append([InlineKeyboardButton(text='📛 Удалить все', callback_data=f'CONVPROXY|DELETE|ALL|{page}')])
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='CONVPROXY|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

