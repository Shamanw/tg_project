from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.exception_phones import *


async def exc_menu_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='➕ Добавить',
                    callback_data='EXC|ADD'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'🚫 [{len(await select_exception_phones())}] Удаление',
                    callback_data='EXC|DELETE|M|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔄',
                    callback_data='EXC|M'
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


async def delete_exceptions_kb(page):
    page_action = f'EXC|DELETE|M'
    writes = await select_exception_phones()
    items_per_page = 30
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    for write in current_writes:
        buttons.append([
            InlineKeyboardButton(
                text=f'🚫 {write.added_at.strftime("%d.%m %H:%M")} • {write.phone_number}',
                callback_data=f'EXC|DELETE|D|{page}|{write.phone_number}'
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='EXC|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

