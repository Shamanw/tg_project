import asyncio

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.main import *
from database.commands.users import *
from database.commands.groups import *
from database.commands.phones_queue import *
from database.commands.scheduler_bot import *
from database.commands.scheduler_text import *
from database.commands.scheduler_groups import *

from utils.misc import get_phone_queue_main_status, time_difference, get_emoji_role, decline_hours_2, decline_day


def manage_menu_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='👤 Управление пользователями',
                    callback_data='MNG|U|M'
                )
            ],
            [
                InlineKeyboardButton(
                    text='👥 Управление группами',
                    callback_data='MNG|G|M'
                )
            ],
            [
                InlineKeyboardButton(
                    text='✉️ Рассылка',
                    callback_data='ADMIN_MANAGE_TEXT'
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


def manage_groups():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='➕ Добавить по ID',
                    callback_data=f'MNG|G|ADD'
                ),
                InlineKeyboardButton(
                    text='➖ Удалить из базы по ID',
                    callback_data=f'MNG|G|DEL'
                )
            ],
            [
                InlineKeyboardButton(
                    text='⚙️ Настройки',
                    callback_data=f'MNG|G|S|M|1'
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


async def groups_settings(page: int = 1):
    page_action = 'MNG|G|S|M'
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
                text=f'{"✅" if write.work_status == 0 else "❌"} {write.group_id} • {write.group_name}',
                callback_data=f'MNG|G|S|T|{page}|{write.group_id}|{1 if write.work_status == 0 else 0}'
            ),]
        )
        buttons.append([
            InlineKeyboardButton(
                text=f'⬆️ Открыть настройки',
                callback_data=f'MNG|G|S|E|{page}|M|{write.group_id}'
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
    
    if page == 1:
        buttons.append([
            InlineKeyboardButton(text='✅ Включить все', callback_data=f'MNG|G|S|AT|{page}|1'),
            InlineKeyboardButton(text='❌ Выключить все', callback_data=f'MNG|G|S|AT|{page}|0')
        ])
    buttons.append(manage_buttons)
    buttons.append([InlineKeyboardButton(text='‹ Назад' ,callback_data='MNG|G|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def groups_otl_kb(group_id, page: int = 1):
    page_action = f'MNG|G|S|E|1|OTL|{group_id}|M'
    writes = await select_many_records(OtlegaGroup, sort_asc='count_days')
    items_per_page = 12
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    if page == 1:
        conn_status = await select_one_record(OtlegaGroupBase, unique_id=111, group_id=group_id)
        buttons.append([
            InlineKeyboardButton(
                text=f'{"✅" if conn_status else ""} Без отлеги',
                callback_data=f'MNG|G|S|E|1|OTL|{group_id}|E|{page}|111|{"D" if conn_status else "A"}'
            ),]
        )
    for write in current_writes:
        conn_status = await select_one_record(OtlegaGroupBase, unique_id=write.unique_id, group_id=group_id)
        buttons.append([
            InlineKeyboardButton(
                text=f'{"✅" if conn_status else ""} {write.count_days} {await decline_day(int(write.count_days))}',
                callback_data=f'MNG|G|S|E|1|OTL|{group_id}|E|{page}|{write.unique_id}|{"D" if conn_status else "A"}'
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
    buttons.append([InlineKeyboardButton(text='‹ Назад' ,callback_data=f'MNG|G|S|E|1|M|{group_id}')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

async def group_manage_kb(write, page: int = 1):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f'{"✅ Включить" if write.work_status == 0 else "❌ Отключить"} группу',
                    callback_data=f'MNG|G|S|E|{page}|T|{write.group_id}|{1 if write.work_status == 0 else 0}'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'🕒 Подключённые подгруппы: {await select_many_records(OtlegaGroupBase, count=True, group_id=write.group_id)} из {await select_many_records(OtlegaGroup, count=True) + 1}',
                    callback_data=f'MNG|G|S|E|{page}|OTL|{write.group_id}|M|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'💲 Установить значение',
                    callback_data=f'MNG|G|S|E|{page}|USD|{write.group_id}|0'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🥷 Статистика клиентов по группе',
                    callback_data=f'STAT|GC|V|{write.group_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='👨‍💻 Статистика дропов по группе',
                    callback_data=f'STAT|G|V|{write.group_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🚫 Удалить группу полностью из базы',
                    callback_data=f'MNG|G|S|E|{page}|D|{write.group_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🔄 Обновить',
                    callback_data=f'MNG|G|S|E|{page}|M|{write.group_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='❌ Закрыть',
                    callback_data='DELETE'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ К списку групп',
                    callback_data=f'MNG|G|S|M|{page}'
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



def slet_timeout_groups_kb():
    callback_data_next = 'CRS|E'
    markup = InlineKeyboardMarkup(
            inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='1',
                    callback_data=f'{callback_data_next}|1|1'
                ),
                InlineKeyboardButton(
                    text='2',
                    callback_data=f'{callback_data_next}|2|1'
                ),
                InlineKeyboardButton(
                    text='3',
                    callback_data=f'{callback_data_next}|3|1'
                ),
                InlineKeyboardButton(
                    text='4',
                    callback_data=f'{callback_data_next}|4|1'
                ),
                InlineKeyboardButton(
                    text='5',
                    callback_data=f'{callback_data_next}|5|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='6',
                    callback_data=f'{callback_data_next}|6|1'
                ),
                InlineKeyboardButton(
                    text='7',
                    callback_data=f'{callback_data_next}|7|1'
                ),
                InlineKeyboardButton(
                    text='8',
                    callback_data=f'{callback_data_next}|8|1'
                ),
                InlineKeyboardButton(
                    text='9',
                    callback_data=f'{callback_data_next}|9|1'
                ),
                InlineKeyboardButton(
                    text='10',
                    callback_data=f'{callback_data_next}|10|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='11',
                    callback_data=f'{callback_data_next}|11|1'
                ),
                InlineKeyboardButton(
                    text='12',
                    callback_data=f'{callback_data_next}|12|1'
                ),
                InlineKeyboardButton(
                    text='13',
                    callback_data=f'{callback_data_next}|13|1'
                ),
                InlineKeyboardButton(
                    text='14',
                    callback_data=f'{callback_data_next}|14|1'
                ),
                InlineKeyboardButton(
                    text='15',
                    callback_data=f'{callback_data_next}|15|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='16',
                    callback_data=f'{callback_data_next}|16|1'
                ),
                InlineKeyboardButton(
                    text='17',
                    callback_data=f'{callback_data_next}|17|1'
                ),
                InlineKeyboardButton(
                    text='18',
                    callback_data=f'{callback_data_next}|18|1'
                ),
                InlineKeyboardButton(
                    text='19',
                    callback_data=f'{callback_data_next}|19|1'
                ),
                InlineKeyboardButton(
                    text='20',
                    callback_data=f'{callback_data_next}|20|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='21',
                    callback_data=f'{callback_data_next}|21|1'
                ),
                InlineKeyboardButton(
                    text='22',
                    callback_data=f'{callback_data_next}|22|1'
                ),
                InlineKeyboardButton(
                    text='23',
                    callback_data=f'{callback_data_next}|23|1'
                ),
                InlineKeyboardButton(
                    text='24',
                    callback_data=f'{callback_data_next}|24|1'
                ),
                InlineKeyboardButton(
                    text='25',
                    callback_data=f'{callback_data_next}|25|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='26',
                    callback_data=f'{callback_data_next}|26|1'
                ),
                InlineKeyboardButton(
                    text='27',
                    callback_data=f'{callback_data_next}|27|1'
                ),
                InlineKeyboardButton(
                    text='28',
                    callback_data=f'{callback_data_next}|28|1'
                ),
                InlineKeyboardButton(
                    text='29',
                    callback_data=f'{callback_data_next}|29|1'
                ),
                InlineKeyboardButton(
                    text='30',
                    callback_data=f'{callback_data_next}|30|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='31',
                    callback_data=f'{callback_data_next}|31|1'
                ),
                InlineKeyboardButton(
                    text='32',
                    callback_data=f'{callback_data_next}|32|1'
                ),
                InlineKeyboardButton(
                    text='33',
                    callback_data=f'{callback_data_next}|33|1'
                ),
                InlineKeyboardButton(
                    text='34',
                    callback_data=f'{callback_data_next}|34|1'
                ),
                InlineKeyboardButton(
                    text='35',
                    callback_data=f'{callback_data_next}|35|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='36',
                    callback_data=f'{callback_data_next}|36|1'
                ),
                InlineKeyboardButton(
                    text='37',
                    callback_data=f'{callback_data_next}|37|1'
                ),
                InlineKeyboardButton(
                    text='38',
                    callback_data=f'{callback_data_next}|38|1'
                ),
                InlineKeyboardButton(
                    text='39',
                    callback_data=f'{callback_data_next}|39|1'
                ),
                InlineKeyboardButton(
                    text='40',
                    callback_data=f'{callback_data_next}|40|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='41',
                    callback_data=f'{callback_data_next}|41|1'
                ),
                InlineKeyboardButton(
                    text='42',
                    callback_data=f'{callback_data_next}|42|1'
                ),
                InlineKeyboardButton(
                    text='43',
                    callback_data=f'{callback_data_next}|43|1'
                ),
                InlineKeyboardButton(
                    text='44',
                    callback_data=f'{callback_data_next}|44|1'
                ),
                InlineKeyboardButton(
                    text='45',
                    callback_data=f'{callback_data_next}|45|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='46',
                    callback_data=f'{callback_data_next}|46|1'
                ),
                InlineKeyboardButton(
                    text='47',
                    callback_data=f'{callback_data_next}|47|1'
                ),
                InlineKeyboardButton(
                    text='48',
                    callback_data=f'{callback_data_next}|48|1'
                ),
                InlineKeyboardButton(
                    text='49',
                    callback_data=f'{callback_data_next}|49|1'
                ),
                InlineKeyboardButton(
                    text='50',
                    callback_data=f'{callback_data_next}|50|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='51',
                    callback_data=f'{callback_data_next}|51|1'
                ),
                InlineKeyboardButton(
                    text='52',
                    callback_data=f'{callback_data_next}|52|1'
                ),
                InlineKeyboardButton(
                    text='53',
                    callback_data=f'{callback_data_next}|53|1'
                ),
                InlineKeyboardButton(
                    text='54',
                    callback_data=f'{callback_data_next}|54|1'
                ),
                InlineKeyboardButton(
                    text='55',
                    callback_data=f'{callback_data_next}|55|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='56',
                    callback_data=f'{callback_data_next}|56|1'
                ),
                InlineKeyboardButton(
                    text='57',
                    callback_data=f'{callback_data_next}|57|1'
                ),
                InlineKeyboardButton(
                    text='58',
                    callback_data=f'{callback_data_next}|58|1'
                ),
                InlineKeyboardButton(
                    text='59',
                    callback_data=f'{callback_data_next}|59|1'
                ),
                InlineKeyboardButton(
                    text='60',
                    callback_data=f'{callback_data_next}|60|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='1 час',
                    callback_data=f'{callback_data_next}|60|1'
                ),
                InlineKeyboardButton(
                    text='1:30 часа',
                    callback_data=f'{callback_data_next}|90|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='2 часа',
                    callback_data=f'{callback_data_next}|120|1'
                ),
                InlineKeyboardButton(
                    text='2:30 часа',
                    callback_data=f'{callback_data_next}|150|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='3 часа',
                    callback_data=f'{callback_data_next}|180|1'
                ),
                InlineKeyboardButton(
                    text='3:30 часа',
                    callback_data=f'{callback_data_next}|210|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='4 часа',
                    callback_data=f'{callback_data_next}|240|1'
                ),
                InlineKeyboardButton(
                    text='4:30 часа',
                    callback_data=f'{callback_data_next}|270|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='5 часов',
                    callback_data=f'{callback_data_next}|300|1'
                ),
                InlineKeyboardButton(
                    text='5:30 часа',
                    callback_data=f'{callback_data_next}|330|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='6 часов',
                    callback_data=f'{callback_data_next}|360|1'
                ),
                InlineKeyboardButton(
                    text='6:30 часа',
                    callback_data=f'{callback_data_next}|390|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='7 часов',
                    callback_data=f'{callback_data_next}|420|1'
                ),
                InlineKeyboardButton(
                    text='7:30 часа',
                    callback_data=f'{callback_data_next}|450|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='8 часов',
                    callback_data=f'{callback_data_next}|480|1'
                ),
                InlineKeyboardButton(
                    text='8:30 часа',
                    callback_data=f'{callback_data_next}|510|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='9 часов',
                    callback_data=f'{callback_data_next}|540|1'
                ),
                InlineKeyboardButton(
                    text='9:30 часа',
                    callback_data=f'{callback_data_next}|570|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='10 часов',
                    callback_data=f'{callback_data_next}|600|1'
                ),
                InlineKeyboardButton(
                    text='10:30 часа',
                    callback_data=f'{callback_data_next}|630|1'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Ввести вручную',
                    callback_data=f'CRS|CUSTOM'
                ),
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

async def slet_groups_kb(page, cross_timeout):
    action = f'CRS|E|{cross_timeout}'
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
                    text=f'{"✅" if write.cross_timeout == cross_timeout else f"[{await decline_hours_2(write.cross_timeout // 60)} {write.cross_timeout % 60} мин.]"} {write.group_name}',
                    callback_data=f'CRS|GE|{cross_timeout}|{page}|{write.group_id}'
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
    buttons.append([InlineKeyboardButton(text='‹ Изменить время', callback_data='CRS|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def phones_manage_kb(page, writes, phone, callback_data_back='START'):
    action = f'PHONE|P|{phone}'
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
                    text=f'{await get_phone_queue_main_status(write.status)} • {write.added_at.strftime("%d.%m.%y %H:%M")}',
                    callback_data=f'PHONE|V|{write.id}'
                ),
            ]
        )

    manage_buttons = []
    if page > 2:
        manage_buttons.append(InlineKeyboardButton(text='⏪ 1', callback_data=f'{action}|1'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    if start > 0: 
        manage_buttons.append(InlineKeyboardButton(text=f'◀️ {page - 1}', callback_data=f'{action}|{page - 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    manage_buttons.append(InlineKeyboardButton(text=f'🔄 {page}', callback_data=f'{action}|{page}'))
    if end < len(writes):
        manage_buttons.append(InlineKeyboardButton(text=f'{page + 1} ▶️', callback_data=f'{action}|{page + 1}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    if page < total_pages and page + 1 != total_pages:
        manage_buttons.append(InlineKeyboardButton(text=f'⏩ {total_pages}', callback_data=f'{action}|{total_pages}'))
    else:
        manage_buttons.append(InlineKeyboardButton(text='\u2063', callback_data='X'))
    buttons.append(manage_buttons)

    buttons.append([InlineKeyboardButton(text='🔍 Искать другой номер', callback_data='PHONE|S')])
    buttons.append([InlineKeyboardButton(text='⬅️ Назад', callback_data=callback_data_back)])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


async def alls_limit_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='0',
                    callback_data=f'ALLSLIMIT|EDIT|0'
                ),
                InlineKeyboardButton(
                    text='5',
                    callback_data=f'ALLSLIMIT|EDIT|5'
                ),
                InlineKeyboardButton(
                    text='10',
                    callback_data=f'ALLSLIMIT|EDIT|10'
                )
            ],
            [
                InlineKeyboardButton(
                    text='15',
                    callback_data=f'ALLSLIMIT|EDIT|15'
                ),
                InlineKeyboardButton(
                    text='20',
                    callback_data=f'ALLSLIMIT|EDIT|20'
                ),
                InlineKeyboardButton(
                    text='25',
                    callback_data=f'ALLSLIMIT|EDIT|25'
                )
            ],
            [
                InlineKeyboardButton(
                    text='30',
                    callback_data=f'ALLSLIMIT|EDIT|30'
                ),
                InlineKeyboardButton(
                    text='50',
                    callback_data=f'ALLSLIMIT|EDIT|50'
                ),
                InlineKeyboardButton(
                    text='70',
                    callback_data=f'ALLSLIMIT|EDIT|70'
                )
            ],
            [
                InlineKeyboardButton(
                    text='100',
                    callback_data=f'ALLSLIMIT|EDIT|100'
                ),
                InlineKeyboardButton(
                    text='150',
                    callback_data=f'ALLSLIMIT|EDIT|150'
                ),
                InlineKeyboardButton(
                    text='200',
                    callback_data=f'ALLSLIMIT|EDIT|200'
                )
            ],
            [
                InlineKeyboardButton(
                    text='300',
                    callback_data=f'ALLSLIMIT|EDIT|300'
                ),
                InlineKeyboardButton(
                    text='400',
                    callback_data=f'ALLSLIMIT|EDIT|400'
                ),
                InlineKeyboardButton(
                    text='500',
                    callback_data=f'ALLSLIMIT|EDIT|500'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Ввести вручную',
                    callback_data=f'ALLSLIMIT|CUSTOM'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data=f'START'
                )
            ]
        ]
    )
    return markup





def manage_users():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🔍 Поиск пользователя по ID',
                    callback_data=f'MNG|U|SEARCH'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='📁 Список пользователей',
                    callback_data=f'MNG|U|L|M|1'
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

async def users_list(page: int = 1):
    page_action = 'MNG|U|L|M'
    writes = await select_users()
    items_per_page = 30
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    for write in current_writes:
        buttons.append([
            InlineKeyboardButton(
                text=f'{await get_emoji_role(write.role)} {write.user_id}{f" • @{write.username}" if write.username else ""} • {write.fullname}',
                callback_data=f'MNG|U|L|V|{page}|U|{write.user_id}'
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
    buttons.append([InlineKeyboardButton(text='‹ Назад' ,callback_data='MNG|U|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

async def user_manage_kb(write, page=1):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f'{"🚫 Заблокировать" if write.is_banned == 0 else "✅ Разблокировать"} ',
                    callback_data=f'MNG|U|L|V|{page}|B|{write.user_id}|{1 if write.is_banned == 0 else 0}'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'{"❌ Выкл. автовывод" if write.auto_withdraw_status == 1 else "✅ Вкл. автовывод"} ',
                    callback_data=f'MNG|U|L|V|{page}|AWS|{write.user_id}|{0 if write.auto_withdraw_status == 1 else 1}'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'👨‍💻 Назначить дропом',
                    callback_data=f'MNG|U|L|V|{page}|R|{write.user_id}|drop'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'🚷 Забрать функционал',
                    callback_data=f'MNG|U|L|V|{page}|R|{write.user_id}|client'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'⭐️ Назначить админом',
                    callback_data=f'MNG|U|L|V|{page}|R|{write.user_id}|admin'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'♻️ Очистить количество автобанов',
                    callback_data=f'MNG|U|L|V|{page}|CLEAR_A_B_C|{write.user_id}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'📁 Все записи',
                    callback_data=f'MNG|U|L|V|{page}|P|{write.user_id}|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'💳 Выводы',
                    callback_data=f'MNG|U|L|V|{page}|WS|{write.user_id}|1'
                )
            ],
            # [
            #     InlineKeyboardButton(
            #         text=f'📸 Коды за сегодня',
            #         callback_data=f'MNG|U|L|V|{page}|Q|{write.user_id}|1'
            #     )
            # ],
            [
                InlineKeyboardButton(
                    text=f'🔢 Установить процент ставки',
                    callback_data=f'MNG|U|L|V|{page}|PERCENT|{write.user_id}|0'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'💲 Установить значение',
                    callback_data=f'MNG|U|L|V|{page}|USD|{write.user_id}|0'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'💵 Изменить баланс',
                    callback_data=f'MNG|U|L|V|{page}|BALANCE|{write.user_id}|0'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'💶 Партнёрский счёт',
                    callback_data=f'MNG|U|L|V|{page}|REF_BALANCE|{write.user_id}|0'
                ),
            ],
            # [
            #     InlineKeyboardButton(
            #         text=f'♻️ Перевести все номера из холда в успешные',
            #         callback_data=f'MNG|U|L|V|{page}|HOLD|{write.user_id}|1'
            #     ),
            # ],
            # [
            #     InlineKeyboardButton(
            #         text=f'🔃 Сбросить автоблокировку',
            #         callback_data=f'MNG|U|L|V|{page}|RCB|{write.user_id}'
            #     )
            # ],
            # [
            #     InlineKeyboardButton(
            #         text=f'⏱ Сбросить дневной лимит',
            #         callback_data=f'MNG|U|L|V|{page}|LIMIT|{write.user_id}'
            #     )
            # ],
            [
                InlineKeyboardButton(
                    text='🔍 Искать другого пользователя',
                    callback_data=f'MNG|U|SEARCH'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'🔄 Обновить',
                    callback_data=f'MNG|U|L|V|{page}|U|{write.user_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='❌ Закрыть',
                    callback_data='DELETE'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ К списку пользователей',
                    callback_data=f'MNG|U|L|M|{page}'
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

async def user_phones_queue_kb(user_id, page = 1, page_list = 1):
    page_action = f'MNG|U|L|V|{page_list}|P|{user_id}'
    writes = await select_phone_queues(drop_id=user_id, sort_desc=True)
    items_per_page = 30
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    for write in current_writes:
        buttons.append([
            InlineKeyboardButton(
                text=f'{await get_phone_queue_main_status(write.status)} • {write.phone_number} • {write.payed_amount if write.payed_amount else 0:.2f}$/{write.buyed_amount if write.buyed_amount else 0:.2f}$ • {write.added_at.strftime("%d.%m %H:%M")}',
                callback_data=f'PHONE|V|{write.id}'
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'MNG|U|L|V|{page_list}|U|{user_id}')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

async def user_qrs_queue_kb(user_id, page = 1, page_list = 1):
    page_action = f'MNG|U|L|V|{page_list}|Q|{user_id}'
    writes = await select_drop_phones_queue_actives(drop_id=user_id)
    items_per_page = 30
    total_pages = (len(writes) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = page * items_per_page
    current_writes = writes[start:end]
    buttons = []
    for write in current_writes:
        buttons.append([
            InlineKeyboardButton(
                text=f'{write.phone_number} • {await time_difference(start=write.confirmed_at, end=write.slet_at) if write.confirmed_at and write.slet_at else ""}',
                callback_data=f'PHONE|V|{write.id}'
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data=f'MNG|U|L|V|{page_list}|U|{user_id}')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup




def invactive_users_menu_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='👨‍💻 Дропы',
                    callback_data='INACTIVE|DROPS|1'
                )
            ],
            # [
            #     InlineKeyboardButton(
            #         text='🥷 Клиенты',
            #         callback_data='INACTIVE|CLIENTS|1'
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

async def invactive_users_kb(page_action, page, writes, start, end, total_pages):
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
    buttons.append([InlineKeyboardButton(text='‹ Назад', callback_data='INACTIVE|M')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup
