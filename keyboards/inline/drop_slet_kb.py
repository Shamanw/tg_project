from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.main import *
from database.commands.phones_queue import *


def slet_menu_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='☠️ Невалид',
                    callback_data='SLET|NL|M|month|1'
                ),
                InlineKeyboardButton(
                    text='💢 Слетевшие',
                    callback_data='SLET|SL|M|month|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='START'
                )
            ],
        ]
    )
    return markup


async def get_drop_list_nevalid_kb(period, total_pages, page=1):
    page_action = f'SLET|NL|M|{period}'
    buttons = []
    buttons.append([
        InlineKeyboardButton(text=f'''{"• " if period == 'today' else ""}Сегодня{" •" if period == 'today' else ""}''', callback_data='SLET|NL|M|today|1'),
        InlineKeyboardButton(text=f'''{"• " if period == 'week' else ""}Неделя{" •" if period == 'week' else ""}''', callback_data='SLET|NL|M|week|1'),
    ])
    buttons.append([
        InlineKeyboardButton(text=f'''{"• " if period == 'month' else ""}Месяц{" •" if period == 'month' else ""}''', callback_data='SLET|NL|M|month|1'),
        InlineKeyboardButton(text=f'''{"• " if period == 'previousmonth' else ""}Пред. месяц{" •" if period == 'previousmonth' else ""}''', callback_data='SLET|NL|M|previousmonth|1'),
    ])
    buttons.append([
        InlineKeyboardButton(text=f'''{"• " if period == '' else ""}Всё время{" •" if period == '' else ""}''', callback_data='SLET|NL|M||1'),
    ])
    manage_buttons = []
    if total_pages > 1:
        manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{page_action}|1') if page > 2 else InlineKeyboardButton(text='\u2063', callback_data='X'))
        manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{page_action}|{page - 1}') if page > 1 else InlineKeyboardButton(text='\u2063', callback_data='X'))
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{page_action}|{page + 1}') if page < total_pages else InlineKeyboardButton(text='\u2063', callback_data='X'))
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{page_action}|{total_pages}') if page < total_pages - 1 else InlineKeyboardButton(text='\u2063', callback_data='X'))
    buttons.append(manage_buttons)
    buttons.append(
        [
            InlineKeyboardButton(
                text='‹ Назад',
                callback_data='SLET|M'
            ),
            InlineKeyboardButton(
                text='Обновить',
                callback_data=f'{page_action}|{page}|u'
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def get_drop_list_slet_kb(period, total_pages, page=1):
    page_action = f'SLET|SL|M|{period}'
    buttons = []
    buttons.append([
        InlineKeyboardButton(text=f'''{"• " if period == 'today' else ""}Сегодня{" •" if period == 'today' else ""}''', callback_data='SLET|SL|M|today|1'),
        InlineKeyboardButton(text=f'''{"• " if period == 'week' else ""}Неделя{" •" if period == 'week' else ""}''', callback_data='SLET|SL|M|week|1'),
    ])
    buttons.append([
        InlineKeyboardButton(text=f'''{"• " if period == 'month' else ""}Месяц{" •" if period == 'month' else ""}''', callback_data='SLET|SL|M|month|1'),
        InlineKeyboardButton(text=f'''{"• " if period == 'previousmonth' else ""}Пред. месяц{" •" if period == 'previousmonth' else ""}''', callback_data='SLET|SL|M|previousmonth|1'),
    ])
    buttons.append([
        InlineKeyboardButton(text=f'''{"• " if period == '' else ""}Всё время{" •" if period == '' else ""}''', callback_data='SLET|SL|M||1'),
    ])
    manage_buttons = []
    if total_pages > 1:
        manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{page_action}|1') if page > 2 else InlineKeyboardButton(text='\u2063', callback_data='X'))
        manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{page_action}|{page - 1}') if page > 1 else InlineKeyboardButton(text='\u2063', callback_data='X'))
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{page_action}|{page + 1}') if page < total_pages else InlineKeyboardButton(text='\u2063', callback_data='X'))
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{page_action}|{total_pages}') if page < total_pages - 1 else InlineKeyboardButton(text='\u2063', callback_data='X'))
    buttons.append(manage_buttons)
    buttons.append(
        [
            InlineKeyboardButton(
                text='‹ Назад',
                callback_data='SLET|M'
            ),
            InlineKeyboardButton(
                text='Обновить',
                callback_data=f'{page_action}|{page}|u'
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)

