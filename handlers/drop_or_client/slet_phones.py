import re

from aiogram import Bot, Router, F, html
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from keyboards.reply.main_kb import *
from keyboards.inline.main_kb import *
from keyboards.inline.misc_kb import *
from keyboards.inline.drop_slet_kb import *

from database.commands.main import *
from database.commands.users import *
from database.commands.phones_queue import *
from database.commands.bot_settings import *
from database.commands.proxy_socks_5 import *
from database.commands.exception_phones import *
from database.commands.withdraws import *

from states.main_modules import *

from utils.misc import *
from utils.tele import *
from utils.additionally_bot import *

from config import *

router = Router()
user_record_locks3 = defaultdict(asyncio.Lock)


@router.callback_query(F.data.startswith('SLET|'))
async def main_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    callback_data = callback.data.split('|')
    action = callback_data[1]
    found_text = ''

    if action == 'M':
        await CallbackEditText(
            callback, 
            text=(
                '<b>Невалид</b> — это аккаунты, которые были заблокированы или восстановлены ДО работы на них'
                '\n\n<b>Слетевшие</b> — это аккаунты, которые были отмечены как слёт в течение 15 минут после взятия в работу. Слёт может быть по нескольким причинам: <b>спам-блок, блокировка, вылет сессии</b>'
                f'\n\n<b>❗️ Если у вас большое количество невалидных или слетевших аккаунтов, вы можете быть заблокированы!</b>'
                '\n\nВыберите тип для просмотра:'
            ),
            reply_markup=slet_menu_kb()
        )

    elif action == 'NL':
        action = callback_data[2]
        if action == 'M':
            period = callback_data[3]
            page = int(callback_data[4])

            total_items = await select_many_records(PhoneQueue, count=True, drop_id=callback.from_user.id, status_in=[23,24], slet_main_at=period, slet_main_at_is_not_none=True)
            items_per_page = 12
            offset = (page - 1) * items_per_page
            total_pages = (total_items + items_per_page - 1) // items_per_page
            writes = await select_many_records(
                PhoneQueue,
                drop_id=callback.from_user.id, 
                sort_desc='slet_main_at', 
                status_in=[23,24], 
                slet_main_at=period, 
                slet_main_at_is_not_none=True,
                limit=items_per_page,
                offset=offset,
            )
            text = ''
            if writes:
                found_text = (
                    f'\n\n<b>→ Найдено записей:</b> <code>{total_items}</code>'
                    f'\n<i>Статус выкупа • Номер • Сумма покупки • Время слёта</i>'
                )
                for write in writes:
                    text += (
                        f'\n<b>{"✅" if write.unban_month_status else "❌"}<code>{write.phone_number}</code>{f" • {famount(write.payed_amount)}$" if write.payed_amount else ""} • {write.slet_main_at.strftime("%d.%m %H:%M")}</b>'
                    )
            else:
                text += f'\nУ вас нет записей за {await get_time_at_period(period)}'
            await CallbackEditText(
                callback,
                text=(
                    f'<b>☠️ Невалид</b>'
                    '\n<i>Аккаунты, которые были заблокированы или восстановлены ДО работы на них</i>'
                    f'{found_text}'
                    f'\n{text}'
                ),
                reply_markup=await get_drop_list_nevalid_kb(period=period, total_pages=total_pages, page=page)
            )

    elif action == 'SL':
        action = callback_data[2]
        if action == 'M':
            period = callback_data[3]
            page = int(callback_data[4])

            total_items = await select_many_records(PhoneQueue, count=True, drop_id=callback.from_user.id, status=18, slet_main_at=period, slet_main_at_is_not_none=True)
            total_items += await select_many_records(PhoneQueue, count=True, drop_id=callback.from_user.id, status=17, alive_status_in=[1,2,3], slet_main_at=period, slet_main_at_is_not_none=True)
            total_items += await select_many_records(PhoneQueue, count=True, drop_id=callback.from_user.id, status=17, alive_status_not_in=[1,2,3], alive_hold_status=1, buyed_at=period, buyed_at_is_not_none=True)

            items_per_page = 12
            offset = (page - 1) * items_per_page
            total_pages = (total_items + items_per_page - 1) // items_per_page
            writes = []
            records = await select_many_records(
                PhoneQueue,
                drop_id=callback.from_user.id, 
                sort_desc='slet_main_at', 
                status=18, 
                slet_main_at=period, 
                slet_main_at_is_not_none=True,
                limit=items_per_page,
                offset=offset,
            )
            if records:
                writes += records
            records = await select_many_records(
                PhoneQueue,
                drop_id=callback.from_user.id, 
                sort_desc='slet_main_at', 
                status=17, 
                alive_status_in=[1,2,3],
                slet_main_at=period, 
                slet_main_at_is_not_none=True,
                limit=items_per_page,
                offset=offset,
            )
            if records:
                writes += records
            records = await select_many_records(
                PhoneQueue,
                drop_id=callback.from_user.id, 
                sort_desc='buyed_at', 
                status=17, 
                alive_status_not_in=[1,2,3],
                alive_hold_status=1,
                buyed_at=period, 
                buyed_at_is_not_none=True,
                limit=items_per_page,
                offset=offset,
            )
            if records:
                writes += records
            text = ''
            if writes:
                found_text = (
                    f'\n\n<b>→ Найдено записей:</b> <code>{total_items}</code>'
                    f'\n<i>Статус выкупа • Номер • Сумма покупки • Время слёта</i>'
                )
                for write in writes:
                    text += (
                        f'\n<b>{"✅" if write.unban_month_status else "❌"} <code>{write.phone_number}</code>{f" • {famount(write.payed_amount)}$" if write.payed_amount else ""} • {write.slet_main_at.strftime("%d.%m %H:%M")}</b>'
                    )
            else:
                text += f'\nУ вас нет записей за {await get_time_at_period(period)}'
            await CallbackEditText(
                callback,
                text=(
                    f'<b>💢 Слетевшие</b>'
                    '\n<i>Аккаунты, которые были отмечены как слёт в течение 15 минут после взятия в работу. Слёт может быть по нескольким причинам: спам-блок, блокировка, вылет сессии</i>'
                    f'{found_text}'
                    f'\n{text}'
                ),
                reply_markup=await get_drop_list_slet_kb(period=period, total_pages=total_pages, page=page)
            )



