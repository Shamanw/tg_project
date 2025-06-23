from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.phones_queue import *


async def added_phones_kb(user_id: int, page: int = 1):
    page_action = 'DROP_WORK|PHONES|M'
    phones = await select_phone_queues(drop_id=user_id, statuses=[0], withdraw_status=0)
    items_per_page = 20
    total_pages = (len(phones) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_phones = phones[start:end]

    buttons = []

    for phone in current_phones:
        buttons.append([InlineKeyboardButton(
            text=f'❌ {phone.added_at.strftime("%d.%m %H:%M")} • {phone.phone_number}',
            callback_data=f'DROP_WORK|PHONES|D|{page}|{phone.id}'
        )])

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
    if end < len(phones):
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{page_action}|{page + 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    if page < total_pages and page + 1 != total_pages:
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{page_action}|{total_pages}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    buttons.append(manage_buttons)
    buttons.append([InlineKeyboardButton(text='‹ Назад' ,callback_data='START')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def withdraw_drop_kb(user_id: int, page: int = 1):
    page_action = 'DROP_WORK|W|M'
    writes = await select_phone_queues(drop_id=user_id, confirmed_status=1, withdraw_status=0, pre_withdraw_statuses=[0,1])
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]

    buttons = []

    for write in current_writes:
        buttons.append([InlineKeyboardButton(
            text=f'{"✅" if write.pre_withdraw_status == 1 else "🔘"} {write.phone_number} • {write.payed_amount:.2f}$',
            callback_data=f'DROP_WORK|W|E|{page}|{write.id}|{0 if write.pre_withdraw_status == 1 else 1}'
        )])

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
    if writes:
        buttons.append([
            InlineKeyboardButton(text='✅ Выбрать все' ,callback_data=f'DROP_WORK|W|ALL|{page}|1'),
            InlineKeyboardButton(text='🔘 Снять все' ,callback_data=f'DROP_WORK|W|ALL|{page}|0')
        ])
    total_withdraw_amount = await select_phone_queues(drop_id=user_id, confirmed_status=1, payed_amount_total=True, withdraw_status=0, pre_withdraw_statuses=[1])
    if total_withdraw_amount:
        buttons.append([InlineKeyboardButton(text=f'⬆️ Вывести {total_withdraw_amount:.2f}$' ,callback_data=f'DROP_WORK|W|S|{page}')])
    buttons.append([InlineKeyboardButton(text='‹ Назад' ,callback_data='START')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup



















def invactive_users_menu_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='За 2 дня',
                    callback_data='INACTIVE|V|2|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='За 3 дня',
                    callback_data='INACTIVE|V|3|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='За 4 дня',
                    callback_data='INACTIVE|V|4|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='За 5 дней',
                    callback_data='INACTIVE|V|5|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='За 6 дней',
                    callback_data='INACTIVE|V|6|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='За 7 дней',
                    callback_data='INACTIVE|V|7|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='\u2063',
                    callback_data='X'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Нулёвые с регой >2 дня',
                    callback_data='INACTIVE|N|2|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Нулёвые с регой >3 дня',
                    callback_data='INACTIVE|N|3|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Нулёвые с регой >4 дня',
                    callback_data='INACTIVE|N|4|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Нулёвые с регой >5 дней',
                    callback_data='INACTIVE|N|5|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Нулёвые с регой >6 дней',
                    callback_data='INACTIVE|N|6|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Нулёвые с регой >7 дней',
                    callback_data='INACTIVE|N|7|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='\u2063',
                    callback_data='X'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Меньше 5 с регой >2 дня',
                    callback_data='INACTIVE|LESS_5|2|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Меньше 5 с регой >3 дня',
                    callback_data='INACTIVE|LESS_5|3|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Меньше 5 с регой >4 дня',
                    callback_data='INACTIVE|LESS_5|4|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Меньше 5 с регой >5 дней',
                    callback_data='INACTIVE|LESS_5|5|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Меньше 5 с регой >6 дней',
                    callback_data='INACTIVE|LESS_5|6|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Меньше 5 с регой >7 дней',
                    callback_data='INACTIVE|LESS_5|7|1'
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

async def invactive_users_kb(page_action, page, writes, start, end, total_pages, days):
    update_page_action = f'{page_action}'
    buttons = []
    manage_buttons = []
    if page > 2:
        manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{update_page_action}|1'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    if start > 0: 
        manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{update_page_action}|{page - 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{update_page_action}|{page}'))
    if end < len(writes):
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{update_page_action}|{page + 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    if page < total_pages and page + 1 != total_pages:
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{update_page_action}|{total_pages}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    buttons.append(manage_buttons)
    buttons.append([InlineKeyboardButton(text='❌ Удалить всех по текущему параметру', callback_data=f'INACTIVE|DD|{days}|1')])
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='INACTIVE|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

async def invactive_users_2_kb(page_action, page, writes, start, end, total_pages, days):
    update_page_action = f'{page_action}'
    buttons = []
    manage_buttons = []
    if page > 2:
        manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{update_page_action}|1'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    if start > 0: 
        manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{update_page_action}|{page - 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{update_page_action}|{page}'))
    if end < len(writes):
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{update_page_action}|{page + 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    if page < total_pages and page + 1 != total_pages:
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{update_page_action}|{total_pages}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    buttons.append(manage_buttons)
    buttons.append([InlineKeyboardButton(text='❌ Удалить всех по текущему параметру', callback_data=f'INACTIVE|D|{days}|1')])
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='INACTIVE|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

async def invactive_users_3_kb(page_action, page, writes, start, end, total_pages, days):
    update_page_action = f'{page_action}'
    buttons = []
    manage_buttons = []
    if page > 2:
        manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{update_page_action}|1'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    if start > 0: 
        manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{update_page_action}|{page - 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{update_page_action}|{page}'))
    if end < len(writes):
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{update_page_action}|{page + 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    if page < total_pages and page + 1 != total_pages:
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{update_page_action}|{total_pages}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    buttons.append(manage_buttons)
    buttons.append([InlineKeyboardButton(text='❌ Удалить всех по текущему параметру', callback_data=f'INACTIVE|D_LESS_5|{days}|1')])
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='INACTIVE|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup
