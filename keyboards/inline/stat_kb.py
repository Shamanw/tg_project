import asyncio

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.users import *
from database.commands.groups import *
from database.commands.phones_queue import *
from database.commands.bot_settings import *

# from utils.misc import 


async def stat_menu_kb():
    bt = await select_bot_setting()
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='👤 Пользователи',
                    callback_data=f'STAT|USERS'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='📈 Прибыль',
                    callback_data=f'STAT|PROFIT'
                ),
                InlineKeyboardButton(
                    text='💸 Пополнения',
                    callback_data=f'STAT|PAYMENTS'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='📊 Общая статистика',
                    callback_data=f'STAT|T'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='ℹ️ Основной бот',
                    callback_data=f'STAT|DEF'
                ),
                InlineKeyboardButton(
                    text='🤖 Клиентский бот',
                    callback_data=f'STAT|CLIENT'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='⭐️ Топ рефоводов за месяц',
                    callback_data=f'STAT|TRM|M|1|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🥷 По клиентам',
                    callback_data=f'STAT|GC|M|7|1'
                ),
                InlineKeyboardButton(
                    text='👨‍💻 По дропам',
                    callback_data=f'STAT|D|M|7|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='💲👥 Изм. знач группам',
                    callback_data='STAT|GUSD|M'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='💲👨‍💻 Изм. знач дропам',
                    callback_data='STAT|USD|M'
                ),
            ],

            # [
            #     InlineKeyboardButton(
            #         text='👥 Статистика по группам',
            #         callback_data=f'STAT|G|M|7|1'
            #     ),
            # ],
            # [
            #     InlineKeyboardButton(
            #         text='➗ Калькулятор по дропам',
            #         callback_data='STAT|C|E'
            #     )
            # ],
            # [
            #     InlineKeyboardButton(
            #         text='💱 Калькулятор дропов',
            #         callback_data='STAT|C2|M'
            #     )
            # ],
            # [
            #     InlineKeyboardButton(
            #         text='📱 Номера в очереди',
            #         callback_data='STAT|P|1'
            #     )
            # ],
            # [
            #     InlineKeyboardButton(
            #         text='📸 Успешные коды',
            #         callback_data='STAT|Q|1'
            #     )
            # ],
            # [
            #     InlineKeyboardButton(
            #         text='🛠 Начавшие работу пользователи',
            #         callback_data='STAT|W|1'
            #     )
            # ],
            # [
            #     InlineKeyboardButton(
            #         text='🔃 Сбросить статистику',
            #         callback_data='STAT|RESET|1'
            #     )
            # ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='START'
                )
            ]
        ]
    )
    return markup


async def stat_clients_groups_kb(page_action, page, null_status):
    update_page_action = f'{page_action}|{null_status}'
    writes = await select_groups(phone_queue_status=True if null_status == 0 else False)
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    
    for write in current_writes:
        success, slet = await asyncio.gather(
            select_phone_queues(group_id=write.group_id, status=17, buyed_at_00_00=True, client_bot=0),
            select_phone_queues(group_id=write.group_id, status=18, slet_at_00_00=True, client_bot=0),
        )
        if null_status == 1 or (null_status == 0 and (success or slet)):
            buttons.append([
                InlineKeyboardButton(
                    text=f'[{len(success)}/{len(slet)}] {write.group_name}',
                    callback_data=f'STAT|GC|V|{write.group_id}'
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
    if page == 1:
        buttons.append([InlineKeyboardButton(text='✅ Вкл. просмотр с нулём', callback_data=f'{page_action}|1|{page}')],)
        buttons.append([InlineKeyboardButton(text='❌ Выкл. просмотр с нулём', callback_data=f'{page_action}|0|{page}')],)
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='STAT|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def stat_groups_kb(page_action, page, null_status):
    update_page_action = f'{page_action}|{null_status}'
    writes = await select_groups(phone_queue_status=True if null_status == 0 else False)
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []

    for write in current_writes:
        success, slet = await asyncio.gather(
            select_phone_queues(group_id=write.group_id, status=17, buyed_at_00_00=True, client_bot=0),
            select_phone_queues(group_id=write.group_id, status=18, slet_at_00_00=True, client_bot=0),
        )
        if null_status == 1 or (null_status == 0 and (success or slet)):
            buttons.append([
                InlineKeyboardButton(
                    text=f'[{len(success)}/{len(slet)}] {write.group_name}',
                    callback_data=f'STAT|G|V|{write.group_id}'
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
    if page == 1:
        buttons.append([InlineKeyboardButton(text='✅ Вкл. просмотр с нулём', callback_data=f'{page_action}|1|{page}')],)
        buttons.append([InlineKeyboardButton(text='❌ Выкл. просмотр с нулём', callback_data=f'{page_action}|0|{page}')],)
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='STAT|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def stat_drops_kb(page_action, page, null_status, writes, start, end, total_pages):
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
        buttons.append([InlineKeyboardButton(text='✅ Вкл. просмотр с нулём', callback_data=f'{page_action}|1|{page}')],)
        buttons.append([InlineKeyboardButton(text='❌ Выкл. просмотр с нулём', callback_data=f'{page_action}|0|{page}')],)
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='STAT|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def stat_phones_queue_kb(page_action, page):
    update_page_action = page_action
    writes = await select_phone_queues(status=12, withdraw_status=1, sort_desc=True)
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
                text=f'[{write.added_at.strftime("%H:%M")}] {write.phone_number}{f" • @{drop_info.username}" if drop_info.username else ""} • {drop_info.fullname}',
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='STAT|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def stat_qrs_queue_kb(page_action, page, writes, start, end, total_pages):
    update_page_action = page_action
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='STAT|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def stat_users_work_kb(page_action, page):
    update_page_action = page_action
    writes = await select_users(is_work=1)
    items_per_page = 80
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []

    for write in current_writes:
        buttons.append([
            InlineKeyboardButton(
                text=f'{write.user_id}{f" • @{write.username}" if write.username else ""} • {write.fullname}',
                callback_data=f'MNG|U|L|G|1|{write.user_id}'
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='STAT|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


def reset_stat_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
            ],
            [
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
            ],
            [
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
            ],
            [
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
                InlineKeyboardButton(text='✅ Сбросить', callback_data='STAT|RESET|4'),
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
            ],
            [
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
            ],
            [
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
            ],
            [
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
                InlineKeyboardButton(text='❌ Отмена', callback_data='STAT|M'),
            ],
        ]
    )
    return markup



async def calc_usd_kb(page_action, page, usd):
    update_page_action = f'{page_action}|M|{usd}'
    writes = await select_users(role='drop')
    items_per_page = 12
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []

    for write in current_writes:
        buttons.append([
            InlineKeyboardButton(
                text=f'[{"✅" if float(write.calc_amount) == usd else float(write.calc_amount)}] {write.user_id}{f" • @{write.username}" if write.username else ""} • {write.fullname}',
                callback_data=f'STAT|C2|USD|L|E|{usd}|{page}|{write.user_id}'
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='STAT|C2|USD|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def calc_unification_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='➕ Создать',
                    callback_data='STAT|C2|DS|C|M|0|1'
                ),
                InlineKeyboardButton(
                    text='➖ Удалить',
                    callback_data='STAT|C2|DS|D|M|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='⚙️ Управление',
                    callback_data='STAT|C2|DS|S|M|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='STAT|C2|M'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹‹ В главное меню',
                    callback_data='START'
                )
            ]
        ]
    )
    return markup





async def set_usd_kb(page, usd):
    update_page_action = f'STAT|USD|C|{usd}'
    writes = await select_users(role='drop')
    items_per_page = 12
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []

    for write in current_writes:
        buttons.append([
            InlineKeyboardButton(
                text=f'[{"✅" if float(write.calc_amount) == usd else float(write.calc_amount)}] {write.user_id}{f" • @{write.username}" if write.username else ""} • {write.fullname}',
                callback_data=f'STAT|USD|S|{usd}|{page}|{write.user_id}'
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
    buttons.append([InlineKeyboardButton(text='☑️ Установить всем', callback_data=f'STAT|USD|ALL|{usd}|{page}')])
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='STAT|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

async def set_usd_group_kb(page, usd):
    update_page_action = f'STAT|GUSD|C|{usd}'
    writes = await select_groups()
    items_per_page = 12
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []

    for write in current_writes:
        buttons.append([
            InlineKeyboardButton(
                text=f'[{"✅" if float(write.calc_amount) == usd else float(write.calc_amount)}] {write.group_id} • {write.group_name}',
                callback_data=f'STAT|GUSD|S|{usd}|{page}|{write.group_id}'
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
    buttons.append([InlineKeyboardButton(text='☑️ Установить всем', callback_data=f'STAT|GUSD|ALL|{usd}|{page}')])
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='STAT|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def stat_referrers_month_kb(total_referrers, page_action, page, sort_type, start, end, total_pages):
    update_page_action = f'{page_action}|{sort_type}'
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
    # if end < len(writes):
    if end < total_referrers:
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{update_page_action}|{page + 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    if page < total_pages and page + 1 != total_pages:
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{update_page_action}|{total_pages}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    buttons.append(manage_buttons)
    buttons.append([
        InlineKeyboardButton(text=f'{"• " if sort_type == 1 else ""}По сумме{" •" if sort_type == 1 else ""}', callback_data=f'{page_action}|1|{page}'),
        InlineKeyboardButton(text=f'{"• " if sort_type == 2 else ""}По юзерам{" •" if sort_type == 2 else ""}', callback_data=f'{page_action}|2|{page}'),
    ])
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='STAT|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup



