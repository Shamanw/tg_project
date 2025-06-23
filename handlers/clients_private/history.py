from aiogram import Bot, Router, F, html
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from database.commands.main import *
from database.commands.users import *
from database.commands.bot_settings import *

from keyboards.inline.misc_kb import *
from keyboards.inline.clients_menu import *

from utils.misc import *
from utils.additionally_bot import *

from config import *


router = Router()


@router.callback_query(F.data.startswith('HISTORY|P|'))
async def callback_handler(callback: CallbackQuery, bot: Bot, state: FSMContext):
    callback_data = callback.data.split('|')
    found_text = ''
    action = callback_data[2]

    if action == 'I':
        await CallbackEditText(
            callback, 
            text=(
                '<b>Выберите нужный раздел:</b>'
                f'\n<i>По умолчанию показаны записи за неделю</i>'
            ), 
            reply_markup=await client_history_menu_kb(user_id=callback.from_user.id)
        )

    elif action == 'N':
        action = callback_data[3]
        if action == 'M':
            period = callback_data[4]
            page = int(callback_data[5])
            total_items = await select_many_records(PhoneQueue, count=True, client_id=callback.from_user.id, client_bot=1, status=17, sort_desc='buyed_at', buyed_at=period)
            if total_items:
                found_text = f'\n\n<b>→ Найдено записей:</b> <code>{total_items}</code>'
            await CallbackEditText(
                callback,
                text=(
                    f'<b>📁 Архив аккаунтов за {await get_time_at_period(period)}</b>'
                    '\n<i>Нажмите на кнопку, чтобы получить подробную информацию о записи</i>'
                    f'{found_text}'
                ),
                reply_markup=await get_client_history_accounts_kb(
                    user_id=callback.from_user.id, 
                    total_items=total_items,
                    period=period,
                    page=page
                )
            )
        elif action == 'O':
            action = callback_data[4]
            primary_id = int(callback_data[5])
            write = await select_phone_queue(primary_id=primary_id)
            if not write:
                return await CallbackAnswer(callback,  text='❓ Аккаунт не найден', show_alert=True)
            if write.client_id != callback.from_user.id:
                return await CallbackAnswer(callback,  text='🔒 Вы не можете просматривать информацию по данному аккаунту.', show_alert=True)
            text = await get_write_info_for_client(write)
            reply_markup = await multi_new_2_2_kb(
                text='Закрыть', callback_data='DELETE',
                text2='Обновить', callback_data2=f'DROP_WORK|P|N|O|U|{write.id}',
            )
            if action == 'V':
                await CallbackMessageAnswer(callback, text=text, reply_markup=reply_markup)
            if action == 'U':
                await CallbackEditText(callback, text=text, reply_markup=reply_markup)

