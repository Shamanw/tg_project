import asyncio

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.main import *
from database.commands.users import *
from database.commands.groups import *
from database.commands.phones_queue import *
from database.commands.bot_settings import *

from utils.misc import get_phone_queue_main_status, famount, archive_types


async def archive_menu_kb():
    tasks = [
        select_many_records(PhoneQueue, count=True, status_in=[12]), # Добавленные
        select_many_records(PhoneQueue, count=True, status_in=[12], otlega_unique_id_is_none=True), # Добавленные без подгрупп
        select_many_records(PhoneQueue, count=True, status_in=[18]), # Слетевшие
        select_many_records(PhoneQueue, count=True, status_in=[19,20,21]), # Удалённые
        select_many_records(PhoneQueue, count=True, status_in=[23, 24]), # Невалидные
        select_many_records(PhoneQueue, count=True, status_in=[22]), # Не приходит смс
        select_many_records(PhoneQueue, count=True, status_in=[0, 1, 6, 8]), # Авторизация
        select_many_records(PhoneQueue, count=True), # Все номера
        select_many_records(PhoneQueue, count=True, status_in=[12], client_bot=0), # Добавленные в дефолтном боте
        select_many_records(PhoneQueue, count=True, status_in=[12], client_bot=1), # Добавленные в клиентском боте
    
        select_many_records(PhoneQueue, count=True, added_at='month'), # Все номера за месяц
        select_many_records(PhoneQueue, count=True, added_at='previousmonth'), # Все номера за пред. месяц
        
        select_many_records(PhoneQueue, count=True, payed_amount_is_not_none=True), # Оплаченные
        select_many_records(PhoneQueue, count=True, status=17), # Выданные
    ]
    
    results = await asyncio.gather(*tasks)
    
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='В пулле:', callback_data='X')],
            [
                InlineKeyboardButton(
                    text=f'✅ [{results[0]}] Все',
                    callback_data='ARCH|A_ALL|drop||1'
                ),
                InlineKeyboardButton(
                    text=f'✔️ [{results[1]}] Без подгрупп',
                    callback_data='ARCH|A_WIOUT|drop||1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'ℹ️ [{results[8]}] Основной бот',
                    callback_data='ARCH|A_DEF|drop||1'
                ),
                InlineKeyboardButton(
                    text=f'🤖 [{results[9]}] Клиентский бот',
                    callback_data='ARCH|A_CLIENT|drop||1'
                ),
            ],
            [InlineKeyboardButton(text='\u2063', callback_data='X')],

            [InlineKeyboardButton(text='Убытки:', callback_data='X')],
            [
                InlineKeyboardButton(
                    text=f'💢 [{results[2]}] Слетевшие',
                    callback_data='ARCH|SLET|group||1'
                ),
                InlineKeyboardButton(
                    text=f'🗑 [{results[3]}] Удалённые',
                    callback_data='ARCH|DEL|drop||1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'☠️ [{results[4]}] Невалидные',
                    callback_data='ARCH|NOT_VALID|drop||1'
                ),
                InlineKeyboardButton(
                    text=f'✉️ [{results[5]}] Не приходит смс',
                    callback_data='ARCH|NOT_SMS|group||1'
                )
            ],
            [InlineKeyboardButton(text='\u2063', callback_data='X')],

            [InlineKeyboardButton(text='Все номера:', callback_data='X')],
            [
                InlineKeyboardButton(
                    text=f'🗓  [{results[10]}] За месяц',
                    callback_data='ARCH|PHONES|time|month|1'
                ),
                InlineKeyboardButton(
                    text=f'↩️ [{results[11]}] За пред. месяц',
                    callback_data='ARCH|PHONES|time|previousmonth|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'♾️ [{results[7]}] За всё время',
                    callback_data='ARCH|PHONES|time||1'
                ),
            ],
            [InlineKeyboardButton(text='\u2063', callback_data='X')],

            [
                InlineKeyboardButton(
                    text=f'💵 [{results[12]}] Оплаченные',
                    callback_data='ARCH|PAYED|drop||1'
                ),
                InlineKeyboardButton(
                    text=f'💷 [{results[13]}] Выданные',
                    callback_data='ARCH|BUYED|group||1'
                ),
            ],

            [
                InlineKeyboardButton(
                    text=f'✍️ [{results[6]}] На авторизации',
                    callback_data='ARCH|AUTH|drop||1'
                ),
            ],

            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='START'
                ),
                InlineKeyboardButton(
                    text='Обновить',
                    callback_data='ARCH|M'
                ),
            ]
        ]
    )
    return markup


async def archive_view_kb(items, action, view_type, period, total_pages, page=1):
    page_action = f'ARCH|{action}|{view_type}|{period}'
    buttons = []; users = {}; groups = {}; view_text = ''
    view_param_at = None
    if view_type == 'time':
        for param_key, param_value in archive_types[action].items():
            if param_key.endswith('_at') and param_value == True:
                view_param_at = param_key
                break

    for item in items:
        phone = item.phone_number[1:]
        payed_amount = f' • 💵{item.payed_amount}' if item.payed_amount else ''
        buyed_amount = f' • 💷{item.buyed_amount}' if item.buyed_amount else ''

        if view_type == 'drop':
            user_id = item.drop_id
            user_data = users.get(user_id)
            if not user_data:
                user_data = await select_one_record(User, user_id=user_id)
                users[user_id] = user_data
            username = f' • @{user_data.username}' if user_data and user_data.username else ''
            fullname = f' • {user_data.fullname}' if user_data and user_data.fullname else ''
            view_text = f'{username}{fullname}'
        elif view_type == 'client':
            user_id = item.client_id
            user_data = users.get(user_id)
            if not user_data:
                user_data = await select_one_record(User, user_id=user_id)
                users[user_id] = user_data
            username = f' • @{user_data.username}' if user_data and user_data.username else ''
            fullname = f' • {user_data.fullname}' if user_data and user_data.fullname else ''
            view_text = f'{username}{fullname}'
        elif view_type == 'group':
            group_id = item.group_id
            group_data = groups.get(group_id)
            if not group_data:
                group_data = await select_one_record(Group, group_id=group_id)
                groups[group_id] = group_data
            group_name = f' • {group_data.group_name}' if group_data and group_data.group_name else f' • {group_id}' if group_id else ''
            view_text = f'{group_name}'
        elif view_type == 'time':
            if action in ['PHONES', 'DEL', 'NOT_VALID', 'AUTH']:
                time_text = f' • {getattr(item, view_param_at).strftime("%d.%m %H:%M")}' if view_param_at and getattr(item, view_param_at) else ''
                status_text = await get_phone_queue_main_status(item.status)
                status_text = f' • {status_text}' if item.status and status_text else ''
                view_text = f'{time_text}{status_text}'
            else:
                view_text = f' • {getattr(item, view_param_at).strftime("%d.%m %H:%M")}' if view_param_at and getattr(item, view_param_at) else ''
        else:
            view_text = ''

        buttons.append([
            InlineKeyboardButton(
                text=f'{phone}{payed_amount}{buyed_amount}{view_text}',
                callback_data=f'PHONE|V|{item.id}'
            ),
        ])

    buttons.append([
        InlineKeyboardButton(text=f'{"•" if view_type == "drop" else "👨‍💻"} Дроп {"•" if view_type == "drop" else ""}', callback_data=f'ARCH|{action}|drop|{period}|{page}'),
        InlineKeyboardButton(text=f'{"•" if view_type == "client" else "🥷"} Клиент {"•" if view_type == "client" else ""}', callback_data=f'ARCH|{action}|client|{period}|{page}'),
        InlineKeyboardButton(text=f'{"•" if view_type == "group" else "👥"} Группа {"•" if view_type == "group" else ""}', callback_data=f'ARCH|{action}|group|{period}|{page}'),
        InlineKeyboardButton(text=f'{"•" if view_type == "time" else "⏳"} Время {"•" if view_type == "time" else ""}', callback_data=f'ARCH|{action}|time|{period}|{page}'),
    ])

    buttons.append([
        InlineKeyboardButton(text=f'{"• " if period == "today" else ""}Сегодня{" •" if period == "today" else ""}', callback_data=f'ARCH|{action}|{view_type}|today|1'),
        InlineKeyboardButton(text=f'{"• " if period == "week" else ""}Неделя{" •" if period == "week" else ""}', callback_data=f'ARCH|{action}|{view_type}|week|1'),
    ])
    buttons.append([
        InlineKeyboardButton(text=f'{"• " if period == "month" else ""}Месяц{" •" if period == "month" else ""}', callback_data=f'ARCH|{action}|{view_type}|month|1'),
        InlineKeyboardButton(text=f'{"• " if period == "previousmonth" else ""}Пред. месяц{" •" if period == "previousmonth" else ""}', callback_data=f'ARCH|{action}|{view_type}|previousmonth|1'),
        InlineKeyboardButton(text=f'{"• " if period == "" else ""}Всё время{" •" if period == "" else ""}', callback_data=f'ARCH|{action}|{view_type}||1'),
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
                callback_data='ARCH|M'
            ),
            InlineKeyboardButton(
                text='Обновить',
                callback_data=f'{page_action}|{page}'
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# async def added_phones_kb(page):
#     update_page_action = 'ARCH|ADDED|M'
#     writes = await select_many_records(PhoneQueue, status=12, sort_desc=True)
#     items_per_page = 30
#     total_pages = (len(writes) + items_per_page - 1) // items_per_page
#     start = (page - 1) * items_per_page
#     end = page * items_per_page
#     current_writes = writes[start:end]
#     buttons = []

#     for write in current_writes:
#         drop_info = await select_user(user_id=write.drop_id)
#         buttons.append([
#             InlineKeyboardButton(
#                 text=f'{write.phone_number} •{f" {famount(write.payed_amount)}$" if write.payed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
#                 callback_data=f'PHONE|V|{write.id}'
#             ),
#         ])

#     manage_buttons = []
#     if page > 2:
#         manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{update_page_action}|1'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if start > 0: 
#         manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{update_page_action}|{page - 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{update_page_action}|{page}'))
#     if end < len(writes):
#         manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{update_page_action}|{page + 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if page < total_pages and page + 1 != total_pages:
#         manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{update_page_action}|{total_pages}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     buttons.append(manage_buttons)
#     buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='ARCH|M')])
#     markup = InlineKeyboardMarkup(inline_keyboard=buttons)
#     return markup


# async def added2_phones_kb(page):
#     update_page_action = 'ARCH|ADDED2|M'
#     writes = await select_many_records(PhoneQueue, status=12, sort_desc=True, otlega_unique_id_is_none=True)
#     items_per_page = 30
#     total_pages = (len(writes) + items_per_page - 1) // items_per_page
#     start = (page - 1) * items_per_page
#     end = page * items_per_page
#     current_writes = writes[start:end]
#     buttons = []

#     for write in current_writes:
#         drop_info = await select_user(user_id=write.drop_id)
#         buttons.append([
#             InlineKeyboardButton(
#                 text=f'{write.phone_number} •{f" {famount(write.payed_amount)}$" if write.payed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
#                 callback_data=f'PHONE|V|{write.id}'
#             ),
#         ])

#     manage_buttons = []
#     if page > 2:
#         manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{update_page_action}|1'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if start > 0: 
#         manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{update_page_action}|{page - 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{update_page_action}|{page}'))
#     if end < len(writes):
#         manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{update_page_action}|{page + 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if page < total_pages and page + 1 != total_pages:
#         manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{update_page_action}|{total_pages}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     buttons.append(manage_buttons)
#     buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='ARCH|M')])
#     markup = InlineKeyboardMarkup(inline_keyboard=buttons)
#     return markup


# async def added3_phones_kb(page):
#     update_page_action = 'ARCH|ADDED3|M'
#     writes = await select_many_records(PhoneQueue, status=12, client_bot=0, sort_desc=True)
#     items_per_page = 30
#     total_pages = (len(writes) + items_per_page - 1) // items_per_page
#     start = (page - 1) * items_per_page
#     end = page * items_per_page
#     current_writes = writes[start:end]
#     buttons = []

#     for write in current_writes:
#         drop_info = await select_user(user_id=write.drop_id)
#         buttons.append([
#             InlineKeyboardButton(
#                 text=f'{write.phone_number} •{f" {famount(write.payed_amount)}$" if write.payed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
#                 callback_data=f'PHONE|V|{write.id}'
#             ),
#         ])

#     manage_buttons = []
#     if page > 2:
#         manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{update_page_action}|1'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if start > 0: 
#         manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{update_page_action}|{page - 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{update_page_action}|{page}'))
#     if end < len(writes):
#         manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{update_page_action}|{page + 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if page < total_pages and page + 1 != total_pages:
#         manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{update_page_action}|{total_pages}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     buttons.append(manage_buttons)
#     buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='ARCH|M')])
#     markup = InlineKeyboardMarkup(inline_keyboard=buttons)
#     return markup


# async def added4_phones_kb(page):
#     update_page_action = 'ARCH|ADDED4|M'
#     writes = await select_many_records(PhoneQueue, status=12, client_bot=1, sort_desc=True)
#     items_per_page = 30
#     total_pages = (len(writes) + items_per_page - 1) // items_per_page
#     start = (page - 1) * items_per_page
#     end = page * items_per_page
#     current_writes = writes[start:end]
#     buttons = []

#     for write in current_writes:
#         drop_info = await select_user(user_id=write.drop_id)
#         buttons.append([
#             InlineKeyboardButton(
#                 text=f'{write.phone_number} •{f" {famount(write.payed_amount)}$" if write.payed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
#                 callback_data=f'PHONE|V|{write.id}'
#             ),
#         ])

#     manage_buttons = []
#     if page > 2:
#         manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{update_page_action}|1'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if start > 0: 
#         manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{update_page_action}|{page - 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{update_page_action}|{page}'))
#     if end < len(writes):
#         manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{update_page_action}|{page + 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if page < total_pages and page + 1 != total_pages:
#         manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{update_page_action}|{total_pages}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     buttons.append(manage_buttons)
#     buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='ARCH|M')])
#     markup = InlineKeyboardMarkup(inline_keyboard=buttons)
#     return markup



# async def slet_phones_kb(page, type, callback_name):
#     update_page_action = f'ARCH|{callback_name}|M'
#     if type == "drop':
#         writes = await select_many_records(PhoneQueue, status_in=[18], sort_desc='slet_at')
#     else:
#         writes = await select_many_records(PhoneQueue, status_in=[18], slet_at="month", sort_desc='slet_at')
#     items_per_page = 30
#     total_pages = (len(writes) + items_per_page - 1) // items_per_page
#     start = (page - 1) * items_per_page
#     end = page * items_per_page
#     current_writes = writes[start:end]
#     buttons = []

#     for write in current_writes:
#         if type in ['drop', 'drop_month']:
#             drop_info = await select_user(user_id=write.drop_id)
#             text = f'{write.phone_number} •{f" {famount(write.payed_amount)}$" if write.payed_amount else ""}{f"/{famount(write.buyed_amount)}$" if write.buyed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}'
#         elif type == "client':
#             client_info = await select_user(user_id=write.client_id)
#             text = f'{write.phone_number} •{f" {famount(write.payed_amount)}$" if write.payed_amount else ""}{f"/{famount(write.buyed_amount)}$" if write.buyed_amount else ""}{f" • @{client_info.username}" if client_info.username else ""} • {client_info.fullname}'
#         elif type == "group':
#             group_info = await select_group(group_id=write.group_id)
#             text = f'{write.phone_number} •{f" {famount(write.payed_amount)}$" if write.payed_amount else ""}{f"/{famount(write.buyed_amount)}$" if write.buyed_amount else ""}{f" • {group_info.group_name}" if group_info and group_info.group_name else write.group_id}'
#         elif type == "time':
#             text = f'{write.phone_number} •{f" {famount(write.payed_amount)}$" if write.payed_amount else ""}{f"/{famount(write.buyed_amount)}$" if write.buyed_amount else ""} • {write.slet_at.strftime("%d.%m %H:%M")}'
#         buttons.append([
#             InlineKeyboardButton(
#                 text=text,
#                 callback_data=f'PHONE|V|{write.id}'
#             ),
#         ])

#     manage_buttons = []
#     if page > 2:
#         manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{update_page_action}|1'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if start > 0: 
#         manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{update_page_action}|{page - 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{update_page_action}|{page}'))
#     if end < len(writes):
#         manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{update_page_action}|{page + 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if page < total_pages and page + 1 != total_pages:
#         manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{update_page_action}|{total_pages}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     buttons.append(manage_buttons)
#     buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='ARCH|M')])
#     markup = InlineKeyboardMarkup(inline_keyboard=buttons)
#     return markup


# async def deleted_phones_kb(page):
#     update_page_action = 'ARCH|DEL|M'
#     writes = await select_many_records(PhoneQueue, status_in=[19,20,21], sort_desc=True)
#     items_per_page = 30
#     total_pages = (len(writes) + items_per_page - 1) // items_per_page
#     start = (page - 1) * items_per_page
#     end = page * items_per_page
#     current_writes = writes[start:end]
#     buttons = []

#     for write in current_writes:
#         drop_info = await select_user(user_id=write.drop_id)
#         buttons.append([
#             InlineKeyboardButton(
#                 text=f'{write.phone_number} •{f" {famount(write.payed_amount)}$" if write.payed_amount else ""}{f"/{famount(write.buyed_amount)}$" if write.buyed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
#                 callback_data=f'PHONE|V|{write.id}'
#             ),
#         ])

#     manage_buttons = []
#     if page > 2:
#         manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{update_page_action}|1'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if start > 0: 
#         manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{update_page_action}|{page - 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{update_page_action}|{page}'))
#     if end < len(writes):
#         manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{update_page_action}|{page + 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if page < total_pages and page + 1 != total_pages:
#         manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{update_page_action}|{total_pages}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     buttons.append(manage_buttons)
#     buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='ARCH|M')])
#     markup = InlineKeyboardMarkup(inline_keyboard=buttons)
#     return markup


# async def not_valid_phones_kb(page):
#     update_page_action = 'ARCH|NOT_VALID|M'
#     writes = await select_many_records(PhoneQueue, status_in=[23, 24], sort_desc=True)
#     items_per_page = 30
#     total_pages = (len(writes) + items_per_page - 1) // items_per_page
#     start = (page - 1) * items_per_page
#     end = page * items_per_page
#     current_writes = writes[start:end]
#     buttons = []

#     for write in current_writes:
#         drop_info = await select_user(user_id=write.drop_id)
#         buttons.append([
#             InlineKeyboardButton(
#                 text=f'{write.phone_number} •{f" {famount(write.payed_amount)}$" if write.payed_amount else ""}{f"/{famount(write.buyed_amount)}$" if write.buyed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
#                 callback_data=f'PHONE|V|{write.id}'
#             ),
#         ])

#     manage_buttons = []
#     if page > 2:
#         manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{update_page_action}|1'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if start > 0: 
#         manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{update_page_action}|{page - 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{update_page_action}|{page}'))
#     if end < len(writes):
#         manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{update_page_action}|{page + 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if page < total_pages and page + 1 != total_pages:
#         manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{update_page_action}|{total_pages}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     buttons.append(manage_buttons)
#     buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='ARCH|M')])
#     markup = InlineKeyboardMarkup(inline_keyboard=buttons)
#     return markup


# async def not_recieve_sms_kb(page):
#     update_page_action = 'ARCH|SMS|M'
#     writes = await select_many_records(PhoneQueue, status=22, sort_desc=True)
#     items_per_page = 30
#     total_pages = (len(writes) + items_per_page - 1) // items_per_page
#     start = (page - 1) * items_per_page
#     end = page * items_per_page
#     current_writes = writes[start:end]
#     buttons = []

#     for write in current_writes:
#         drop_info = await select_user(user_id=write.drop_id)
#         buttons.append([
#             InlineKeyboardButton(
#                 text=f'{write.phone_number} •{f" {famount(write.payed_amount)}$" if write.payed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
#                 callback_data=f'PHONE|V|{write.id}'
#             ),
#         ])

#     manage_buttons = []
#     if page > 2:
#         manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{update_page_action}|1'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if start > 0: 
#         manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{update_page_action}|{page - 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{update_page_action}|{page}'))
#     if end < len(writes):
#         manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{update_page_action}|{page + 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if page < total_pages and page + 1 != total_pages:
#         manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{update_page_action}|{total_pages}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     buttons.append(manage_buttons)
#     buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='ARCH|M')])
#     markup = InlineKeyboardMarkup(inline_keyboard=buttons)
#     return markup


# async def auth_phones_kb(page):
#     update_page_action = 'ARCH|AUTH|M'
#     writes = await select_many_records(PhoneQueue, status_in=[0, 1, 6, 8], sort_desc=True)
#     items_per_page = 30
#     total_pages = (len(writes) + items_per_page - 1) // items_per_page
#     start = (page - 1) * items_per_page
#     end = page * items_per_page
#     current_writes = writes[start:end]
#     buttons = []

#     for write in current_writes:
#         drop_info = await select_user(user_id=write.drop_id)
#         buttons.append([
#             InlineKeyboardButton(
#                 text=f'{write.phone_number} •{f" {famount(write.payed_amount)}$" if write.payed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
#                 callback_data=f'PHONE|V|{write.id}'
#             ),
#         ])

#     manage_buttons = []
#     if page > 2:
#         manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{update_page_action}|1'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if start > 0: 
#         manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{update_page_action}|{page - 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{update_page_action}|{page}'))
#     if end < len(writes):
#         manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{update_page_action}|{page + 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if page < total_pages and page + 1 != total_pages:
#         manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{update_page_action}|{total_pages}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     buttons.append(manage_buttons)
#     buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='ARCH|M')])
#     markup = InlineKeyboardMarkup(inline_keyboard=buttons)
#     return markup


# async def all_phones_kb(page):
#     update_page_action = 'ARCH|ALL|M'
#     writes = await select_many_records(PhoneQueue, sort_desc=True)
#     items_per_page = 30
#     total_pages = (len(writes) + items_per_page - 1) // items_per_page
#     start = (page - 1) * items_per_page
#     end = page * items_per_page
#     current_writes = writes[start:end]
#     buttons = []

#     for write in current_writes:
#         drop_info = await select_user(user_id=write.drop_id)
#         buttons.append([
#             InlineKeyboardButton(
#                 text=f'{write.phone_number} • {await get_phone_queue_main_status(write.status)} •{f" {famount(write.payed_amount)}$" if write.payed_amount else ""}{f"/{famount(write.buyed_amount)}$" if write.buyed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
#                 callback_data=f'PHONE|V|{write.id}'
#             ),
#         ])

#     manage_buttons = []
#     if page > 2:
#         manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{update_page_action}|1'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if start > 0: 
#         manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{update_page_action}|{page - 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{update_page_action}|{page}'))
#     if end < len(writes):
#         manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{update_page_action}|{page + 1}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     if page < total_pages and page + 1 != total_pages:
#         manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{update_page_action}|{total_pages}'))
#     else:
#         manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
#     buttons.append(manage_buttons)
#     buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='ARCH|M')])
#     markup = InlineKeyboardMarkup(inline_keyboard=buttons)
#     return markup

