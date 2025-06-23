from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.main import *
from database.commands.users import *
from database.commands.groups import *
from database.commands.phones_queue import *
from database.commands.bot_settings import *

from utils.misc import get_phone_queue_main_status, decline_day, calculate_hold_time, famount


async def otlega_menu_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f'➕ Добавить',
                    callback_data='OTLEGA|ADD'
                ),
                InlineKeyboardButton(
                    text=f'➖ Удалить',
                    callback_data='OTLEGA|DEL|M|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'👁 Просмотр',
                    callback_data='OTLEGA|EDIT|M|1'
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


async def add_otlega_group_kb(count_accounts, count_days):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f'✅ Да',
                    callback_data=f'OTLEGA|CREATE|{count_accounts}|{count_days}|1'
                ),
                InlineKeyboardButton(
                    text=f'❌ Нет',
                    callback_data=f'OTLEGA|CREATE|{count_accounts}|{count_days}|0'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='OTLEGA|ADD'
                )
            ]
        ]
    )
    return markup


async def delete_otlega_groups_kb(page):
    update_page_action = 'OTLEGA|DEL|M'
    writes = await select_many_records(OtlegaGroup, sort_asc='count_days')
    items_per_page = 12
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []

    for write in current_writes:
        in_hold = len(await select_many_records(PhoneQueue, otlega_unique_id=write.unique_id, status_in=[12, 14, 15], set_at_less=int(write.count_days)))
        total_accounts = len(await select_many_records(PhoneQueue, otlega_unique_id=write.unique_id, status_in=[12, 14, 15]))
        is_ready = total_accounts - in_hold
        is_ready = is_ready if is_ready else 0
        buttons.append([
            InlineKeyboardButton(
                text=f'❌ {write.count_days} {await decline_day(int(write.count_days))} • ✅ {is_ready} • ⏳ {in_hold} • 👤 {total_accounts}/{write.count_accounts} ❌',
                callback_data=f'OTLEGA|DEL|D|{page}|{write.unique_id}'
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='OTLEGA|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def edit_otlega_groups_kb(page):
    update_page_action = 'OTLEGA|EDIT|M'
    writes = await select_many_records(OtlegaGroup, sort_asc='count_days')
    items_per_page = 12
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []

    if page == 1:
        buttons.append([
            InlineKeyboardButton(
                text=f'Слетевшие: {await select_many_records(PhoneQueue, count=True, tdata_status=0, status=18, alive_status=9)}',
                callback_data=f'OTLEGA|EDIT|E|{page}|222|M'
            ),
        ])
        buttons.append([
            InlineKeyboardButton(
                text=f'Отработки: {await select_many_records(PhoneQueue, count=True, tdata_status=0, status=18, alive_status_in=[2,3])}',
                callback_data=f'OTLEGA|EDIT|E|{page}|333|M'
            ),
        ])
        is_ready = await select_many_records(PhoneQueue, count=True, otlega_unique_id_is_none=True, status=12)
        buttons.append([
            InlineKeyboardButton(
                text=f'Без отлеги: {is_ready}',
                callback_data=f'OTLEGA|EDIT|E|{page}|111|M'
            ),
        ])

    for write in current_writes:
        in_hold = await select_many_records(PhoneQueue, count=True, otlega_unique_id=write.unique_id, status_in=[12, 14, 15], set_at_less=int(write.count_days))
        total_accounts = await select_many_records(PhoneQueue, count=True, otlega_unique_id=write.unique_id, status_in=[12, 14, 15])
        is_ready = total_accounts - in_hold
        is_ready = is_ready if is_ready else 0
        buttons.append([
            InlineKeyboardButton(
                text=f'{write.count_days} {await decline_day(int(write.count_days))} • ✅ {is_ready} • ⏳ {in_hold} • 👤 {total_accounts}/{write.count_accounts}',
                callback_data=f'OTLEGA|EDIT|E|{page}|{write.unique_id}|M'
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='OTLEGA|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def otlega_edit_kb(unique_id, write):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[      
            [
                InlineKeyboardButton(
                    text='✅ Готовые',
                    callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|ACCS1|1'
                ),
                InlineKeyboardButton(
                    text='⏳ В холде',
                    callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|ACCS2|1'
                ),
                InlineKeyboardButton(
                    text='❓ Осталось',
                    callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|ACCS_LEFT|1'
                ),
            ],    
            [
                InlineKeyboardButton(
                    text=f'{"🟢" if write.refill_accounts_status else "🔘"} Автодобавление',
                    callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|ED|refill_accounts_status|{0 if write.refill_accounts_status else 1}'
                ),
                InlineKeyboardButton(
                    text='🗂 Выгрузить',
                    callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|TDATA|M'
                ),
            ],    
            [
                InlineKeyboardButton(
                    text='✏️ Изменить кол-во аккаунтов',
                    callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|EDIT_COUNT'
                ),
            ],    
            [
                InlineKeyboardButton(
                    text='⏩ Сбросить пропуск записей',
                    callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|ED|skip_updates_status|0'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🗄⬆️ Выгрузить в клиентский бот',
                    callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|UNLOAD|M|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🗄⬇️ Забрать из клиентского бота',
                    callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|TAKE|M|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'👥 Подключенные группы: {len(await select_many_records(OtlegaGroupBase, unique_id=unique_id))} из {len(await select_many_records(Group))}',
                    callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|G|M|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔄',
                    callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|M'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='OTLEGA|EDIT|M|1'
                )
            ]
        ]
    )
    return markup



async def otlega_edit_222_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='✅ Готовые',
                    callback_data=f'OTLEGA|EDIT|E|1|222|ACCS222|1'
                ),
                InlineKeyboardButton(
                    text='⌛️ В холде',
                    callback_data=f'OTLEGA|EDIT|E|1|222|ACCS222HOLD|1'
                ),
                InlineKeyboardButton(
                    text='❓ Осталось',
                    callback_data=f'OTLEGA|EDIT|E|1|222|ACCS_LEFT|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🗂 Выгрузить',
                    callback_data=f'OTLEGA|EDIT|E|1|222|TDATA|M'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🗄⬆️ Выгрузить в клиентский бот',
                    callback_data=f'OTLEGA|EDIT|E|1|222|UNLOAD|M|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🗄⬇️ Забрать из клиентского бота',
                    callback_data=f'OTLEGA|EDIT|E|1|222|TAKE|M|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔄',
                    callback_data=f'OTLEGA|EDIT|E|1|222|M'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='OTLEGA|EDIT|M|1'
                )
            ]
        ]
    )
    return markup

async def accs_otlega_groups_222_kb(page):
    update_page_action = f'OTLEGA|EDIT|E|1|222|ACCS222'
    writes = await select_many_records(PhoneQueue, tdata_status=0, status=18, alive_status=9, sort_asc='slet_at')
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    for write in current_writes:
        drop_info = await select_user(user_id=write.drop_id)
        buttons.append([
            InlineKeyboardButton(
                text=f'{write.phone_number}{f" • {famount(write.payed_amount)}$" if write.payed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'OTLEGA|EDIT|E|1|222|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

async def accs_otlega_groups_222_hold_kb(page):
    update_page_action = f'OTLEGA|EDIT|E|1|222|ACCS222HOLD'
    writes = await select_many_records(PhoneQueue, status=18, alive_status_in=[0,10], sort_asc='slet_at')
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    for write in current_writes:
        drop_info = await select_user(user_id=write.drop_id)
        buttons.append([
            InlineKeyboardButton(
                text=f'{write.phone_number}{f" • {famount(write.payed_amount)}$" if write.payed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'OTLEGA|EDIT|E|1|222|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

async def accs_left_222_kb(page):
    update_page_action = f'OTLEGA|EDIT|E|1|222|ACCS_LEFT'
    writes = await select_many_records(PhoneQueue, status=18, alive_status_in=[0,10], sort_asc='slet_at')
    # writes = await select_many_records(PhoneQueue, status=18, alive_status_in=[0,10], sort_asc='slet_at')
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    for write in current_writes:
        buttons.append([
            InlineKeyboardButton(
                text=f'{write.phone_number}{f" • {famount(write.payed_amount)}$" if write.payed_amount else ""} • {await calculate_hold_time(write.slet_at, 7)}',
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'OTLEGA|EDIT|E|1|222|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup






async def otlega_edit_333_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='✅ Готовые',
                    callback_data=f'OTLEGA|EDIT|E|1|333|ACCS333|1'
                ),
                InlineKeyboardButton(
                    text='🗂 Выгрузить',
                    callback_data=f'OTLEGA|EDIT|E|1|333|TDATA|M'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🗄⬆️ Выгрузить в клиентский бот',
                    callback_data=f'OTLEGA|EDIT|E|1|333|UNLOAD|M|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🗄⬇️ Забрать из клиентского бота',
                    callback_data=f'OTLEGA|EDIT|E|1|333|TAKE|M|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔄',
                    callback_data=f'OTLEGA|EDIT|E|1|333|M'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='OTLEGA|EDIT|M|1'
                )
            ]
        ]
    )
    return markup

async def accs_otlega_groups_333_kb(page):
    update_page_action = f'OTLEGA|EDIT|E|1|333|ACCS333'
    writes = await select_many_records(PhoneQueue, tdata_status=0, status=18, alive_status_in=[2,3], sort_asc='slet_at')
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    for write in current_writes:
        drop_info = await select_user(user_id=write.drop_id)
        buttons.append([
            InlineKeyboardButton(
                text=f'{write.phone_number}{f" • {famount(write.payed_amount)}$" if write.payed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'OTLEGA|EDIT|E|1|333|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup










async def otlega_edit_default_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='✅ Готовые',
                    callback_data=f'OTLEGA|EDIT|E|1|111|DEFACCS1|1'
                ),
                InlineKeyboardButton(
                    text='🗂 Выгрузить',
                    callback_data=f'OTLEGA|EDIT|E|1|111|TDATA|M'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🗄⬆️ Выгрузить в клиентский бот',
                    callback_data=f'OTLEGA|EDIT|E|1|111|UNLOAD|M|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🗄⬇️ Забрать из клиентского бота',
                    callback_data=f'OTLEGA|EDIT|E|1|111|TAKE|M|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'👥 Подключенные группы: {len(await select_many_records(OtlegaGroupBase, unique_id=111))} из {len(await select_many_records(Group))}',
                    callback_data=f'OTLEGA|EDIT|E|1|111|G|M|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔄',
                    callback_data=f'OTLEGA|EDIT|E|1|111|M'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='OTLEGA|EDIT|M|1'
                )
            ]
        ]
    )
    return markup

async def defaccs1_otlega_groups_kb(page):
    update_page_action = f'OTLEGA|EDIT|E|1|111|DEFACCS1'
    writes = await select_many_records(PhoneQueue, otlega_unique_id_is_none=True, status=12, sort_asc='set_at')
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    for write in current_writes:
        drop_info = await select_user(user_id=write.drop_id)
        buttons.append([
            InlineKeyboardButton(
                text=f'{write.phone_number}{f" • {famount(write.payed_amount)}$" if write.payed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'OTLEGA|EDIT|E|1|111|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def accs1_otlega_groups_kb(page, unique_id, count_days):
    update_page_action = f'OTLEGA|EDIT|E|1|{unique_id}|ACCS1'
    writes = await select_many_records(PhoneQueue, otlega_unique_id=unique_id, status_in=[12, 14, 15], set_at_more=count_days, sort_asc='set_at')
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    for write in current_writes:
        drop_info = await select_user(user_id=write.drop_id)
        buttons.append([
            InlineKeyboardButton(
                text=f'{write.phone_number}{f" • {famount(write.payed_amount)}$" if write.payed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

async def accs2_otlega_groups_kb(page, unique_id, count_days):
    update_page_action = f'OTLEGA|EDIT|E|1|{unique_id}|ACCS2'
    writes = await select_many_records(PhoneQueue, otlega_unique_id=unique_id, status_in=[12, 14, 15], set_at_less=count_days, sort_asc='set_at')
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    for write in current_writes:
        drop_info = await select_user(user_id=write.drop_id)
        buttons.append([
            InlineKeyboardButton(
                text=f'{write.phone_number}{f" • {famount(write.payed_amount)}$" if write.payed_amount else ""}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

async def accs_left_otlega_groups_kb(page, unique_id, count_days):
    update_page_action = f'OTLEGA|EDIT|E|1|{unique_id}|ACCS_LEFT'
    writes = await select_many_records(PhoneQueue, otlega_unique_id=unique_id, status_in=[12, 14, 15], set_at_less=count_days, sort_asc='set_at')
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    for write in current_writes:
        buttons.append([
            InlineKeyboardButton(
                text=f'{write.phone_number}{f" • {famount(write.payed_amount)}$" if write.payed_amount else ""} • {await calculate_hold_time(write.set_at, count_days)}',
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def groups_otlega_groups_kb(page, unique_id):
    update_page_action = f'OTLEGA|EDIT|E|1|{unique_id}|G|M'
    writes = await select_many_records(Group, sort_asc='group_name')
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    for write in current_writes:
        conn_status = await select_one_record(OtlegaGroupBase, unique_id=unique_id, group_id=write.group_id)
        buttons.append([
            InlineKeyboardButton(
                text=f'{"✅ " if conn_status else ""}{write.group_id} • {write.group_name}',
                callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|G|E|{page}|{write.group_id}|{"D" if conn_status else "A"}'
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
    if page == 1:
        buttons.append([
            InlineKeyboardButton(text='✅ Подключить все', callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|G|ALL|{page}|A'),
            InlineKeyboardButton(text='❌ Отключить все', callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|G|ALL|{page}|D')
        ])
    buttons.append(manage_buttons)
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup




async def take_phones_kb(page, unique_id):
    update_page_action = f'OTLEGA|EDIT|E|1|{unique_id}|TAKE|M'
    if unique_id == 111:
        qwrite = None
        writes = await select_many_records(PhoneQueue, otlega_unique_id_is_none=True, status=12, sort_asc='set_at', client_bot=1)
    elif unique_id == 222:
        qwrite = None
        writes = await select_many_records(PhoneQueue, tdata_status=0, status=18, alive_status=9, sort_asc='set_at', client_bot=1)
    elif unique_id == 333:
        qwrite = None
        writes = await select_many_records(PhoneQueue, tdata_status=0, status=18, alive_status_in=[2,3], sort_asc='set_at', client_bot=1)
    else:
        qwrite = await select_one_record(OtlegaGroup, unique_id=unique_id)
        writes = await select_many_records(PhoneQueue, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), sort_asc='set_at', client_bot=1)
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    for write in current_writes:
        buttons.append([
            InlineKeyboardButton(
                text=f'↪️ {write.phone_number}{f" • {famount(write.payed_amount)}$" if write.payed_amount else ""} • {write.buyed_amount if write.buyed_amount else 0:.2f}$',
                callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|TAKE|E|{page}|{write.id}'
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
    if page == 1:
        buttons.append([
            InlineKeyboardButton(text='☑️↪️ Забрать все', callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|TAKE|ALL|{page}'),
        ])
    buttons.append(manage_buttons)
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'OTLEGA|EDIT|E|1|{unique_id}|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup



