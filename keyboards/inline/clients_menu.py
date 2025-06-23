import asyncio

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.main import *

from utils.misc import decline_day, famount, get_time_at_period


async def profile_menu_kb(user):
    buttons = []
    

    buttons.append([
        InlineKeyboardButton(
            text='💳 Пополнить',
            callback_data=f'deposit'
        ),
        InlineKeyboardButton(
            text=f'📁 Архив',
            callback_data=f'HISTORY|P|I'
        )
    ])
    buttons.append([
        InlineKeyboardButton(
            text='🔗 Привязка баланса',
            callback_data=f'PROFILE|LINK|M'
        ),
    ])
    if user.def_unique_id:
        buttons.append([
            InlineKeyboardButton(
                text='❌ Убрать лот по умолчанию',
                callback_data=f'PROFILE|LOT_CLEAR'
            ),
        ])
        
    buttons.append([
        InlineKeyboardButton(
            text=f'‹ Назад',
            callback_data=f'START'
        ),
        InlineKeyboardButton(
            text=f'Обновить',
            callback_data=f'PROFILE|M'
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def partners_menu_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Вывод средств',
                    callback_data=f'WDRW|M'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'‹ Назад',
                    callback_data=f'START'
                ),
            ]
        ]
    )
    return markup


async def catalog_choose_kb():
    buttons = []
    total = 0
    otrabotka = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True)
    if otrabotka:
        total += otrabotka
        buttons.append([
            InlineKeyboardButton(
                text=f'Отработанные: {otrabotka} шт.',
                callback_data='CATALOG|MENU|333'
            )
        ])
    sletevshie = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True)
    if sletevshie:
        total += sletevshie
        buttons.append([
            InlineKeyboardButton(
                text=f'Отработанные с отлегой: {sletevshie} шт.',
                callback_data='CATALOG|MENU|222'
            )
        ])
    bez_otlegi = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True)
    if bez_otlegi:
        total += bez_otlegi
        buttons.append([
            InlineKeyboardButton(
                text=f'Без отлеги: {bez_otlegi} шт.',
                callback_data='CATALOG|MENU|111'
            )
        ])
    qwrites = await select_many_records(OtlegaGroup)
    if qwrites:
        qwrites = qwrites[:95]
        for qwrite in qwrites:
            accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id=qwrite.unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True)
            if accs_count:
                total += accs_count
                buttons.append([
                    InlineKeyboardButton(
                        text=f'Отлега {qwrite.count_days} {await decline_day(int(qwrite.count_days))}: {accs_count} шт.',
                        callback_data=f'CATALOG|MENU|{qwrite.unique_id}'
                    )
                ])
    if not total:
        buttons.append([
            InlineKeyboardButton(
                text='Нет доступных аккаунтов',
                callback_data='X'
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text=f'‹ Назад',
            callback_data=f'START'
        ),
        InlineKeyboardButton(
            text=f'Обновить',
            callback_data=f'CATALOG|M'
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def catalog_menu_kb(unique_id, qwrite):
    buttons = []
    if unique_id == 111:
        writes_count = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True)
    elif unique_id == 222:
        writes_count = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True)
    elif unique_id == 333:
        writes_count = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True)
    else:
        writes_count = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True)

    if writes_count:
        buttons.append([
            InlineKeyboardButton(
                text='🔢 Купить tdata/session',
                callback_data=f'CATALOG|COUNT|M|{unique_id}'
            ),
        ])
        buttons.append([
            InlineKeyboardButton(
                text='🔑 Войти по СМС',
                callback_data=f'CATALOG|SMS|GET|{unique_id}'
            ),
        ])
        buttons.append([
            InlineKeyboardButton(
                text='📌 Установить как лот по умолчанию',
                callback_data=f'CATALOG|LOT_SET|{unique_id}'
            ),
        ])

    buttons.append([
        InlineKeyboardButton(
            text=f'‹ Назад',
            callback_data='CATALOG|M'
        ),
        InlineKeyboardButton(
            text=f'Обновить',
            callback_data=f'CATALOG|MENU|{unique_id}'
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def client_history_menu_kb(user_id):
    main_period = 'week'
    count_phones = await asyncio.gather(
        select_many_records(PhoneQueue, count=True, client_id=user_id, client_bot=1, status=17, sort_desc='buyed_at'),
    )
    inline_keyboard = []
    inline_keyboard.append(
        [
            InlineKeyboardButton(
                text=f'Аккаунты: {count_phones}',
                callback_data=f'HISTORY|P|N|M|{main_period}|1'
            ),
        ]
    )
    inline_keyboard.append(
        [
            InlineKeyboardButton(
                text='‹ Назад',
                callback_data='PROFILE|M'
            ),
            InlineKeyboardButton(
                text='Обновить',
                callback_data='HISTORY|P|I'
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

async def get_client_history_accounts_kb(user_id, total_items, period, page=1):
    page_action = f'HISTORY|P|N|M|{period}'
    items_per_page = 12
    offset = (page - 1) * items_per_page
    total_pages = (total_items + items_per_page - 1) // items_per_page
    writes = await select_many_records(
        PhoneQueue,
        client_id=user_id, 
        client_bot=1, 
        status=17,
        sort_desc='buyed_at', 
        limit=items_per_page,
        offset=offset,
        buyed_at=period
    )
    buttons = []
    if writes:
        for write in writes:
            buttons.append([
                InlineKeyboardButton(
                    text=f'{write.buyed_at.strftime("%d.%m %H:%M")} • {write.phone_number} • {famount(write.buyed_amount)}$',
                    callback_data=f'HISTORY|P|N|O|V|{write.id}'
                ),]
            )
    else:
        buttons.append([
            InlineKeyboardButton(
                text=f'У вас нет аккаунтов за {await get_time_at_period(period)}',
                callback_data='X'
            ),]
        )
    buttons.append([
        InlineKeyboardButton(text=f'''{"• " if period == 'today' else ""}За сегодня{" •" if period == 'today' else ""}''', callback_data='HISTORY|P|N|M|today|1|x'),
        InlineKeyboardButton(text=f'''{"• " if period == 'week' else ""}За неделю{" •" if period == 'week' else ""}''', callback_data='HISTORY|P|N|M|week|1|x'),
    ])
    buttons.append([
        InlineKeyboardButton(text=f'''{"• " if period == 'month' else ""}За месяц{" •" if period == 'month' else ""}''', callback_data='HISTORY|P|N|M|month|1|x'),
        InlineKeyboardButton(text=f'''{"• " if period == '' else ""}За всё время{" •" if period == '' else ""}''', callback_data='HISTORY|P|N|M||1|x'),
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
                callback_data='HISTORY|P|I'
            ),
            InlineKeyboardButton(
                text='Обновить',
                callback_data=f'{page_action}|{page}|u'
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)




async def client_groups_connections_kb(user_id, page):
    page_action = 'PROFILE|LINK|E|M'
    writes = await select_many_records(LinkGroup, user_id=user_id, sort_desc='added_at')
    items_per_page = 10
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    if current_writes:
        for write in current_writes:
            buttons.append([
                InlineKeyboardButton(
                    text=f'❌ {write.group_id} • 🔗 {write.added_at.strftime("%d.%m.%y %H:%M")}',
                    callback_data=f'PROFILE|LINK|E|D|{page}|{write.group_id}'
                ),]
            )
    else:
        buttons.append([
            InlineKeyboardButton(
                text='Нет активных подключений',
                callback_data='X'
            ),]
        )
    manage_buttons = []
    if total_pages > 1:
        manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{page_action}|1') if page > 2 else InlineKeyboardButton(text='\u2063', callback_data='X'))
        manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{page_action}|{page - 1}') if page > 1 else InlineKeyboardButton(text='\u2063', callback_data='X'))
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{page_action}|{page + 1}') if page < total_pages else InlineKeyboardButton(text='\u2063', callback_data='X'))
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{page_action}|{total_pages}') if page < total_pages - 1 else InlineKeyboardButton(text='\u2063', callback_data='X'))
    buttons.append(manage_buttons)
    if total_pages > 1:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f'Страница {page} из {total_pages}',
                    callback_data='X'
                ),
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text='‹ Назад',
                callback_data='PROFILE|LINK|M'
            ),
            InlineKeyboardButton(
                text='Обновить',
                callback_data=f'{page_action}|1'
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


