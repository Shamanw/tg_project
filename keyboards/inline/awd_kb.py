from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.users import *
from database.commands.groups import *
from database.commands.withdraws import *
from database.commands.phones_queue import *
from database.commands.bot_settings import *


async def awd_menu_kb():
    bt = await select_bot_setting()
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f'{"✅ Вкл." if bt.auto_withdraw_status == 0 else "❌ Выкл."} автовывод',
                    callback_data=f'AWD|E|{1 if bt.auto_withdraw_status == 0 else 0}'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'💳 Выводы [⏳ {len(await select_withdraws(withdraw_status=0))} • ✅ {len(await select_withdraws(withdraw_status=1))} • ❌ {len(await select_withdraws(withdraw_status=2))}]',
                    callback_data='AWD|W|M|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='💸 Выплаченные номера',
                    callback_data='AWD|S|M|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🔄',
                    callback_data='AWD|M'
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


async def awd_drops_kb(page_action, page, null_status, writes, start, end, total_pages):
    update_page_action = f'{page_action}|{null_status}'
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
    if page == 1:
        buttons.append([InlineKeyboardButton(text='✅ Вкл. просмотр с нулём', callback_data=f'{page_action}|T|{page}')],)
        buttons.append([InlineKeyboardButton(text='❌ Выкл. просмотр с нулём', callback_data=f'{page_action}|F|{page}')],)
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='AWD|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def withdraw_writes_kb(page):
    update_page_action = 'AWD|S|M'
    writes = await select_phone_queues(withdraw_status=1, sort_desc=True)
    items_per_page = 30
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []

    for write in current_writes:
        drop_info = await select_user(user_id=write.drop_id)
        buttons.append([
            InlineKeyboardButton(
                text=f'{write.phone_number} • {write.payed_amount:.2f}${f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
                callback_data=f'PHONE|V|{write.id}'
            ),
        ])

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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='AWD|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def manage_autowithdraw_drops_kb(page):
    update_page_action = 'AWD|V|M'
    writes = await select_users(role='drop')
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []

    for write in current_writes:
        buttons.append([
            InlineKeyboardButton(
                text=f'{"✅" if write.auto_withdraw == 0 else "❌"}{f" • @{write.username}" if write.username else ""} • {write.fullname}',
                callback_data=f'AWD|V|E|{page}|{write.user_id}|{1 if write.auto_withdraw == 0 else 0}'
            ),
        ])

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
    buttons.append([InlineKeyboardButton(text='❌ Выключить всем', callback_data=f'AWD|V|ALL|{page}|0')])
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='AWD|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def withdraws_kb(page):
    update_page_action = 'AWD|W|M'
    writes = await select_withdraws(sort_desc=True)
    items_per_page = 30
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []

    for write in current_writes:
        buttons.append([
            InlineKeyboardButton(
                text=f'{"❌" if write.withdraw_status == 2 else "✅" if write.withdraw_status == 1 else "⏳"} {write.id} • {write.amount:.2f}$ ({len(write.phones)}) • {write.user_id}',
                callback_data=f'AWD|W|V|{write.id}'
            ),
        ])
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='AWD|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

