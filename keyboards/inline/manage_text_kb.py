from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.users import *
from database.commands.groups import *
from database.commands.scheduler_text import *
from database.commands.scheduler_groups import *
from database.commands.scheduler_bot import *

from utils.misc import decline_hours, get_emoji_role


def manage_text_menu_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='➕ Добавить текст',
                    callback_data='MTT|TEXT|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='➖ Удалить текст',
                    callback_data='MTT|DL|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='ℹ️ Список',
                    callback_data='MTT|M|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='MNG|M'
                )
            ]
        ]
    )
    return markup


def manage_text_kb(unique_id):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='⚙️ Настройки',
                    callback_data=f'MTT|E|1|{unique_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='📝 Изменить текст',
                    callback_data=f'MTT|EDIT|0|{unique_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='⏳ Выбрать период отправки',
                    callback_data=f'MTT|P|1|{unique_id}| |0|0|0'
                )
            ],
            [
                InlineKeyboardButton(
                    text='👁 Показать обработанный вариант',
                    callback_data=f'MTT|VIEW|0|{unique_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='⚙️ Показать необработанный вариант',
                    callback_data=f'MTT|VIEW|1|{unique_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='✉️ Перейти ко списку всех текстов',
                    callback_data='MTT|M|1'
                )
            ],[
                InlineKeyboardButton(
                    text='👤 Добавить упоминания пользователей в текст',
                    callback_data=f'MTT|U|1|{unique_id}|1|M|0'

                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='MTT|TEXT|1'
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


def edit_text_full_kb(unique_id):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='👁 Показать обработанный вариант',
                    callback_data=f'MTT|VIEW|0|{unique_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='⚙️ Показать необработанный вариант',
                    callback_data=f'MTT|VIEW|1|{unique_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='❌ Удалить текст',
                    callback_data=f'MTT|D|1|{unique_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data=f'MTT|E|1|{unique_id}'
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


async def edit_text_kb(unique_id, page, write):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='⬆️ 👥 Отправить прямо сейчас во все подключенные группы',
                    callback_data=f'MTT|NOW|{page}|{unique_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='👥 Удалить группы',
                    callback_data=f'MTT|GL|{page}|{unique_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🤖 Удалить рассылки по боту',
                    callback_data=f'MTT|BL|{page}|{unique_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'🤖 ✅ Включить все рассылки по боту с выбранным текстом',
                    callback_data=f'MTT|BMNG|{page}|{unique_id}|ON'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'🤖 ⛔️ Выключить все рассылки по боту с выбранным текстом',
                    callback_data=f'MTT|BMNG|{page}|{unique_id}|OFF'
                )
            ],
            [
                InlineKeyboardButton(
                    text='⏳ Выбрать период отправки',
                    callback_data=f'MTT|P|{page}|{unique_id}| |0|0|0'
                )
            ],
            [
                InlineKeyboardButton(
                    text='✅ Включить превью ссылки' if write.disable_web_page_preview else '🚫 Выключить превью ссылки',
                    callback_data=f'MTT|PW|{page}|{unique_id}|0' if write.disable_web_page_preview else f'MTT|PW|{page}|{unique_id}|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='👁 Показать обработанный вариант',
                    callback_data=f'MTT|VIEW|0|{unique_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='⚙️ Показать необработанный вариант',
                    callback_data=f'MTT|VIEW|1|{unique_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='👤 Добавить упоминания пользователей в текст',
                    callback_data=f'MTT|U|{page}|{unique_id}|1|M|0'

                )
            ],
            [
                InlineKeyboardButton(
                    text='📝 Изменить текст',
                    callback_data=f'MTT|EDIT|0|{unique_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='❌ Удалить текст',
                    callback_data=f'MTT|D|{page}|{unique_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🔄 Обновить',
                    callback_data=f'MTT|E|{page}|{unique_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data=f'MTT|M|{page}'
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


async def list_texts(callback_data: str = 'START', text: str = '‹ Назад', page: int = 1):
    action = f'MTT|M'
    writes = await select_scheduler_texts()
    if writes:
        writes = writes[::-1]
    items_per_page = 12
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]

    buttons = []

    for write in current_writes:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f'🕒 {write.added_at.strftime("%d.%m %H:%M")} • 👥 {len(await select_scheduler_groups(unique_id=write.unique_id))} • 🤖 {len(await select_scheduler_bots(unique_id=write.unique_id))} • {write.text}',
                    callback_data=f'MTT|E|{page}|{write.unique_id}'
                ),
            ]
        )
    manage_buttons = []

    if page > 2:
        manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{action}|1'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    if start > 0: 
        manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{action}|{page - 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{action}|{page}'))

    if end < len(writes):
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{action}|{page + 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    if page < total_pages and page + 1 != total_pages:
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{action}|{total_pages}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    buttons.append(manage_buttons)
    buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def get_inline_button(n1, n2, action, period, period_minutes, period_type, symbol):
    num_buttons = []
    for n in range(n1, n2):
        emoji = ''
        if int(period_type) == 0:
            cdata = f'{eval(f"{period} {symbol} {n}") if symbol != " " else n}|{period_minutes}'
            if symbol == " ":
                emoji = f'{"✅" if int(period) == n else ""}'
        elif int(period_type) == 1:
            cdata = f'{period}|{eval(f"{period_minutes} {symbol} {n}") if symbol != " " else n}'
            if symbol == " ":
                emoji = f'{"✅" if int(period_minutes) == n else ""}'
        num_buttons.append(
            InlineKeyboardButton(
                text=f'{emoji} {symbol if symbol != " " else "="}{n}',
                callback_data=f'{action}|{cdata}|{period_type}'
            ),
        )
    return num_buttons

async def period_text_kb(unique_id, page, period, period_minutes, symbol, period_type, bot):
    buttons = []
    buttons.append([InlineKeyboardButton(text='⬆️ Перейти к группам', callback_data=f'MTT|G|{page}|{unique_id}|{period}|{period_minutes}|M')])
    buttons.append(
        [
            InlineKeyboardButton(
                text=f'🤖 Рассылка по боту',
                callback_data=f'MTT|BP|{page}|{unique_id}|{period}|{period_minutes}|M|0'
            ),
        ]
    )
    action = f'MTT|P|{page}|{unique_id}'
    buttons.append(
        [
            InlineKeyboardButton(
                text=f'{"✅" if int(period_type) == 0 else ""} Настройка часов',
                callback_data=f'{action}|{symbol}|{period}|{period_minutes}|0'
            )
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text=f'{"✅" if int(period_type) == 1 else ""} Настройка минут',
                callback_data=f'{action}|{symbol}|{period}|{period_minutes}|1'
            )
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(text=f'{"✅" if symbol == " " else ""} =', callback_data=f'{action}| |{period}|{period_minutes}|{period_type}'),
            InlineKeyboardButton(text=f'{"✅" if symbol == "+" else ""} +', callback_data=f'{action}|+|{period}|{period_minutes}|{period_type}'),
            InlineKeyboardButton(text=f'{"✅" if symbol == "-" else ""} -', callback_data=f'{action}|-|{period}|{period_minutes}|{period_type}'),
            InlineKeyboardButton(text=f'{"✅" if symbol == "*" else ""} *', callback_data=f'{action}|*|{period}|{period_minutes}|{period_type}'),
        ]
    )
    action = f'MTT|P|{page}|{unique_id}|{symbol}'
    n_1 = 0
    n_2 = 5
    for n in range(0, 13):
        num_buttons = await get_inline_button(n_1, n_2, action, period, period_minutes, period_type, symbol)
        buttons.append(num_buttons)
        n_1 += 5
        n_2 += 5
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'MTT|E|{page}|{unique_id}')])
    buttons.append([InlineKeyboardButton(text='‹‹ В главное меню', callback_data='START')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def groups_text_kb(unique_id, page, period, period_minutes):
    action = f'MTT|G'
    added_groups_data = await select_scheduler_groups(unique_id=unique_id, period=period, period_minutes=period_minutes)
    added_groups = []
    for w in added_groups_data:
        if w:
            added_groups.append(w.group_id)
    writes = await select_groups()
    if writes:
        writes = writes[::-1]
    items_per_page = 12
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]

    buttons = []

    for write in current_writes:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f'{"❌" if write.group_id in added_groups else "✅"} {write.group_id} • {write.group_name}',
                    callback_data=f'MTT|G|{page}|{unique_id}|{period}|{period_minutes}|N|{write.group_id}' if write.group_id in added_groups else f'MTT|G|{page}|{unique_id}|{period}|{period_minutes}|Y|{write.group_id}'
                ),
            ]
        )
    manage_buttons = []

    if page > 2:
        manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{action}|1|{unique_id}|{period}|{period_minutes}|M'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    if start > 0: 
        manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{action}|{page - 1}|{unique_id}|{period}|{period_minutes}|M'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|M'))

    if end < len(writes):
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{action}|{page + 1}|{unique_id}|{period}|{period_minutes}|M'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    if page < total_pages and page + 1 != total_pages:
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{action}|{total_pages}|{unique_id}|{period}|{period_minutes}|M'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    buttons.append(manage_buttons)
    buttons.append([InlineKeyboardButton(text='‹ Изменить период', callback_data=f'MTT|P|1|{unique_id}| |0|0|0')])
    buttons.append([InlineKeyboardButton(text='‹‹ В главное меню', callback_data='START')])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def delete_texts(callback_data: str = 'START', text: str = '‹ Назад', page: int = 1):
    action = f'MTT|DL'
    writes = await select_scheduler_texts()
    if writes:
        writes = writes[::-1]
    items_per_page = 12
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]

    buttons = []

    for write in current_writes:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f'❌ 🕒 {write.added_at.strftime("%d.%m %H:%M")} • 👥 {len(await select_scheduler_groups(unique_id=write.unique_id))} • 🤖 {len(await select_scheduler_bots(unique_id=write.unique_id))} • {write.text}',
                    callback_data=f'MTT|DD|{page}|{write.unique_id}'
                ),
            ]
        )
    manage_buttons = []

    if page > 2:
        manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{action}|1'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    if start > 0: 
        manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{action}|{page - 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{action}|{page}'))

    if end < len(writes):
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{action}|{page + 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    if page < total_pages and page + 1 != total_pages:
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{action}|{total_pages}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    buttons.append(manage_buttons)
    buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def delete_groups_text_kb(unique_id, page):
    action = f'MTT|GL'
    writes = await select_scheduler_groups(unique_id=unique_id)
    if writes:
        writes = writes[::-1]
    items_per_page = 12
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]

    buttons = []

    for write in current_writes:
        group_info = await select_group(group_id=write.group_id)
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f'❌ {write.group_id} • ⏳ {write.period} • 🔢 {write.period_minutes} {f"• {group_info.group_name}" if group_info else ""}',
                    callback_data=f'MTT|GD|{page}|{unique_id}|{write.group_id}|{write.period}|{write.period_minutes}'
                ),
            ]
        )
    manage_buttons = []

    if page > 2:
        manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{action}|1|{unique_id}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    if start > 0: 
        manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{action}|{page - 1}|{unique_id}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{action}|{page}|{unique_id}'))

    if end < len(writes):
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{action}|{page + 1}|{unique_id}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    if page < total_pages and page + 1 != total_pages:
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{action}|{total_pages}|{unique_id}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    buttons.append(manage_buttons)
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'MTT|E|1|{unique_id}')])
    buttons.append([InlineKeyboardButton(text='‹‹ В главное меню', callback_data='START')])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def delete_bots_text_kb(unique_id, page):
    action = f'MTT|BL'
    writes = await select_scheduler_bots(unique_id=unique_id)
    if writes:
        writes = writes[::-1]
    items_per_page = 12
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]

    buttons = []

    for write in current_writes:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f'❌ ⏳ {write.period} • 🔢 {write.period_minutes}',
                    callback_data=f'MTT|BD|{page}|{unique_id}|{write.period}|{write.period_minutes}'
                ),
            ]
        )
    manage_buttons = []

    if page > 2:
        manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{action}|1|{unique_id}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    if start > 0: 
        manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{action}|{page - 1}|{unique_id}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{action}|{page}|{unique_id}'))

    if end < len(writes):
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{action}|{page + 1}|{unique_id}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    if page < total_pages and page + 1 != total_pages:
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{action}|{total_pages}|{unique_id}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    buttons.append(manage_buttons)
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'MTT|E|1|{unique_id}')])
    buttons.append([InlineKeyboardButton(text='‹‹ В главное меню', callback_data='START')])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def add_mention_kb(unique_id, page, page_back, write, users_filter, mention_ids):
    action = f'MTT|U|{page_back}|{unique_id}'
    role = None
    is_work = None
    is_banned = None
    if users_filter == 1:
        role = 'client'
    elif users_filter == 2:
        role = 'drop'
    elif users_filter == 3:
        role = 'admin'
    elif users_filter == 4:
        is_work = 1
    elif users_filter == 5:
        is_work = 0
    elif users_filter == 6:
        is_banned = 0
    elif users_filter == 7:
        is_banned = 1
    
    if users_filter == 8:
        writes = []
        for u in mention_ids:
            i = await select_user(user_id=u)
            if i:
                writes.append(i)
    else:
        writes = await select_users(role=role, is_work=is_work, is_banned=is_banned)
    if writes:
        writes = writes[::-1]
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]

    buttons = []

    for write in current_writes:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f'{"❌" if write.user_id in mention_ids else "✅"}{f" {await get_emoji_role(write.role)}" if users_filter in (0, 4, 5, 6, 7) else ""} • {write.user_id}{f" • @{write.username}" if write.username else ""} • {write.fullname}',
                    callback_data=f'MTT|U|{page_back}|{unique_id}|{page}|A|{users_filter}|{write.user_id}'
                ),
            ]
        )
    manage_buttons = []

    if page > 2:
        manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{action}|1|M|{users_filter}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    if start > 0: 
        manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{action}|{page - 1}|M|{users_filter}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{action}|{page}|M|{users_filter}'))

    if end < len(writes):
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{action}|{page + 1}|M|{users_filter}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    if page < total_pages and page + 1 != total_pages:
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{action}|{total_pages}|M|{users_filter}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    buttons.append(manage_buttons)
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 0 else ""} все', callback_data=f'MTT|U|{page_back}|{unique_id}|{page}|M|0')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 1 else ""} клиенты', callback_data=f'MTT|U|{page_back}|{unique_id}|{page}|M|1')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 2 else ""} дропы', callback_data=f'MTT|U|{page_back}|{unique_id}|{page}|M|2')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 3 else ""} админы', callback_data=f'MTT|U|{page_back}|{unique_id}|{page}|M|3')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 4 else ""} начавшие работу', callback_data=f'MTT|U|{page_back}|{unique_id}|{page}|M|4')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 5 else ""} закончившие работу', callback_data=f'MTT|U|{page_back}|{unique_id}|{page}|M|5')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 6 else ""} не забанненые', callback_data=f'MTT|U|{page_back}|{unique_id}|{page}|M|6')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 7 else ""} забаненные', callback_data=f'MTT|U|{page_back}|{unique_id}|{page}|M|7')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 8 else ""} добавленные', callback_data=f'MTT|U|{page_back}|{unique_id}|{page}|M|8')])
    buttons.append([InlineKeyboardButton(text='👁 Показать обработанный вариант', callback_data=f'MTT|VIEW|0|{unique_id}')])
    buttons.append([InlineKeyboardButton(text='⚙️ Показать необработанный вариант', callback_data=f'MTT|VIEW|1|{unique_id}')])
    buttons.append([InlineKeyboardButton(text='📝 Изменить текст', callback_data=f'MTT|EDIT|{page_back}|{unique_id}')])
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'MTT|E|{page_back}|{unique_id}')])
    buttons.append([InlineKeyboardButton(text='‹‹ В главное меню', callback_data='START')])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def add_users_kb(unique_id, page, period, period_minutes, writes, ids_remove, users_filter, enable_status):
    action = f'MTT|BP'
    if writes:
        writes = writes[::-1]
    items_per_page = 20
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]

    buttons = []

    for write in current_writes:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f'{"✅" if write.user_id in ids_remove else "❌"}{f" {await get_emoji_role(write.role)}" if users_filter in (0, 4, 5, 6, 7) else ""} • {write.user_id}{f" • @{write.username}" if write.username else ""} • {write.fullname}',
                    callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|Y|{users_filter}|{write.user_id}' if write.user_id in ids_remove else f'{action}|{page}|{unique_id}|{period}|{period_minutes}|N|{users_filter}|{write.user_id}'
                ),
            ]
        )
    manage_buttons = []

    if page > 2:
        manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{action}|1|{unique_id}|{period}|{period_minutes}|M|{users_filter}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    if start > 0: 
        manage_buttons.append(InlineKeyboardButton(text=f'⬅️ {page - 1}', callback_data=f'{action}|{page - 1}|{unique_id}|{period}|{period_minutes}|M|{users_filter}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|M|{users_filter}'))

    if end < len(writes):
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ➡️', callback_data=f'{action}|{page + 1}|{unique_id}|{period}|{period_minutes}|M|{users_filter}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    if page < total_pages and page + 1 != total_pages:
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{action}|{total_pages}|{unique_id}|{period}|{period_minutes}|M|{users_filter}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))

    buttons.append(manage_buttons)
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 0 else ""} все', callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|M|0')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 1 else ""} клиенты', callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|M|1')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 2 else ""} дропы', callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|M|2')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 3 else ""} админы', callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|M|3')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 4 else ""} начавшие работу', callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|M|4')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 5 else ""} закончившие работу', callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|M|5')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 6 else ""} не забанненые', callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|M|6')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 7 else ""} забаненные', callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|M|7')])
    buttons.append([InlineKeyboardButton(text=f'{"👁" if users_filter == 8 else ""} исключённые', callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|M|8')])
    buttons.append([InlineKeyboardButton(text='✅ Добавить в рассылку всех по фильтру', callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|ALLY|{users_filter}')])
    buttons.append([InlineKeyboardButton(text='❌ Исключить из рассылки всех по фильтру', callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|ALLN|{users_filter}')])
    buttons.append([InlineKeyboardButton(text='⚙️ Показать необработанный вариант', callback_data=f'MTT|VIEW|1|{unique_id}')])
    buttons.append([InlineKeyboardButton(text='📝 Изменить текст', callback_data=f'MTT|EDIT|1|{unique_id}')])
    buttons.append([InlineKeyboardButton(text='❌ Удалить текст из рассылки по боту', callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|D|{users_filter}')])
    buttons.append(
        [
            InlineKeyboardButton(
                text=f'{"✅ Включить" if enable_status == 0 else "⛔️ Выключить"} рассылку по боту',
                callback_data=f'{action}|{page}|{unique_id}|{period}|{period_minutes}|ON|{users_filter}' if enable_status == 0 else f'{action}|{page}|{unique_id}|{period}|{period_minutes}|OFF|{users_filter}'
            ),
        ]
    )
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'MTT|E|1|{unique_id}')])
    buttons.append([InlineKeyboardButton(text='‹‹ В главное меню', callback_data='START')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

