from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from keyboards.reply.main_kb import *
from keyboards.inline.main_kb import *
from keyboards.inline.misc_kb import *
from keyboards.inline.stat_kb import *

from database.tables import *
from database.commands.users import *
from database.commands.groups import *
from database.commands.phones_queue import *
from database.commands.exception_phones import *
from database.commands.bot_settings import *
from database.commands.calc_temp import *
from database.commands.calc_temp_drops import *
# from database.commands.allow_search_phone_types import *

from states.main_modules import *

from utils.misc import *
from utils.additionally_bot import *

from config import *

import os
import aiofiles
from aiofiles.tempfile import NamedTemporaryFile
import csv


router = Router()




@router.callback_query(F.data.startswith('STAT'))
async def callback_query(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    callback_data = callback.data.split('|')
    action = callback_data[1]
    if action == 'M':
        await CallbackEditText(
            callback,
            text=(
                '<b>📊 Статистика</b>'
                '\n\nВыберите действие:'
            ),
            reply_markup=stat_menu_kb()
        )


    elif action == 'GC':
        action = callback_data[2]
        if action == 'M':
            null_status = callback_data[3]
            page = int(callback_data[4])
            await CallbackEditText(
                callback,
                text=(
                    '<b>🥷 Статистика по клиентам</b>'
                    f'\n\n<b>• Отображение:</b> <code>[успешные/в холде/неудачные/повторы/пропуски] название группы</code>'
                    f'\n\n<b>• Просмотр списка с нулём:</b> <code>{"✅ вкл." if null_status == "T" else "❌ выкл."}</code>'
                    '\n\nВыберите группу:'
                ),
                reply_markup=await stat_clients_groups_kb(page_action='STAT|GC|M', page=page, null_status=null_status)
            )

        elif action == 'V':
            async def send_large_message(bot, chat_id, text, reply_markup=None):
                try:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
                except Exception as e:
                    if "message is too long" in str(e).lower():
                        pass
                        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        # unique_id = str(uuid.uuid4())[:8]
                        # filename = f"temp_message_{timestamp}_{unique_id}.txt"
                        # temp_path = os.path.join("temp", filename)
                        # try:
                        #     os.makedirs("temp", exist_ok=True)
                        #     with open(temp_path, 'w', encoding='utf-8') as f:
                        #         f.write(text.replace("<b>", "").replace("</b>", "").replace("<code>", "").replace("</code>", ""))
                        #     await BotSendDocument(
                        #         bot,
                        #         chat_id=chat_id,
                        #         document=FSInputFile(temp_path),
                        #         reply_markup=reply_markup
                        #     )
                        # finally:
                        #     if os.path.exists(temp_path):
                        #         os.remove(temp_path)
                    else:
                        raise

            group_id = int(callback_data[3])
            group_info = await select_group(group_id=group_id)
            if not group_info:
                return await CallbackAnswer(callback, '⚠️ Группа не найдена!', show_alert=True)
            
            writes = await select_phone_queues(group_id=group_id, statuses=[4, 5, 6, 7])
            if not writes:
                return await CallbackAnswer(callback, '❌ Нет записей за сегодня по данной группе!', show_alert=True)
            
            users = {}
            totals = {'4_1': 0, '4_0': 0, '5': 0, '6': 0, '7': 0}
            
            for write in writes:
                user_id = write.client_id
                status = write.status
                if user_id not in users:
                    users[user_id] = {'4_1': 0, '4_0': 0, '5': 0, '6': 0, '7': 0}
                    
                if status == 4:
                    key = '4_1' if write.waiting_confirm_status == 1 else '4_0'
                    users[user_id][key] += 1
                    totals[key] += 1
                elif status in [5, 6, 7]:
                    key = str(status)
                    users[user_id][key] += 1
                    totals[key] += 1

            message = (
                f'<b>👁 Статистика клиентов в группе /gid{str(group_id).replace("-", "")} '
                f'[{html.escape(group_info.group_name)}] за сегодня</b>\n\n'
                f'<b>• Отображение:</b> <code>успешные/в холде/неудачные/повторы/пропуски</code>\n'
            )
            
            for user_id, counts in users.items():
                user_info = await select_user(user_id=user_id)
                user_name = f"@{user_info.username}" if user_info.username else f"<code>{html.escape(user_info.fullname)}</code>"
                message += (
                    f'\n<b>👨‍💻 /uid{user_id} [{user_name}]:</b> '
                    f'{counts["4_1"]}/{counts["4_0"]}/{counts["5"]}/{counts["6"]}/{counts["7"]}'
                )
            
            message += (
                f'\n\n<b>ℹ️ Тотал:</b> {totals["4_1"]}/{totals["4_0"]}/{totals["5"]}'
                f'/{totals["6"]}/{totals["7"]}'
            )

            await send_large_message(
                bot,
                chat_id=callback.from_user.id,
                text=message,
                reply_markup=multi_kb(callback_data='DELETE', text='❌ Закрыть')
            )



    elif action == 'G':
        action = callback_data[2]
        if action == 'M':
            null_status = callback_data[3]
            page = int(callback_data[4])
            await CallbackEditText(
                callback,
                text=(
                    '<b>👥 Статистика по группам</b>'
                    f'\n\n<b>• Отображение:</b> <code>[успешные/в холде/неудачные/повторы/пропуски] название группы</code>'
                    f'\n\n<b>• Просмотр списка с нулём:</b> <code>{"✅ вкл." if null_status == "T" else "❌ выкл."}</code>'
                    '\n\nВыберите группу:'
                ),
                reply_markup=await stat_groups_kb(page_action='STAT|G|M', page=page, null_status=null_status)
            )

        elif action == 'V':
            group_id = int(callback_data[3])
            group_info = await select_group(group_id=group_id)
            if not group_info:
                return await CallbackAnswer(callback, '⚠️ Группа не найдена!', show_alert=True)
            writes = await select_phone_queues(group_id=group_id, statuses=[4, 5, 6, 7])
            if not writes:
                return await CallbackAnswer(callback, '❌ Нет записей за сегодня по данной группе!', show_alert=True)
            users = {}
            total_4_1 = 0
            total_4_0 = 0
            total_5 = 0
            total_6 = 0
            total_7 = 0
            for write in writes:
                user_id = write.drop_id
                status = write.status
                if user_id not in users:
                    users[user_id] = {'4_1': 0, '4_0': 0, '5': 0, '6': 0, '7': 0}
                if status == 4 and write.waiting_confirm_status == 1:
                    users[user_id]['4_1'] += 1
                    total_4_1 += 1
                elif status == 4 and write.waiting_confirm_status == 0:
                    users[user_id]['4_0'] += 1
                    total_4_0 += 1
                elif status == 5:
                    users[user_id]['5'] += 1
                    total_5 += 1
                elif status == 6:
                    users[user_id]['6'] += 1
                    total_6 += 1
                elif status == 7:
                    users[user_id]['7'] += 1
                    total_7 += 1
            result = ''
            for user_id, counts in users.items():
                user_info = await select_user(user_id=user_id)
                result += (
                    f'\n<b>👨‍💻 /uid{user_id} [{f"@{user_info.username}" if user_info.username else f"<code>{html.escape(user_info.fullname)}</code>"}]:</b> '
                    f'{counts["4_1"]}/{counts["4_0"]}/{counts["5"]}/{counts["6"]}/{counts["7"]}' 
                )
            await CallbackMessageAnswer(
                callback,
                text=(
                    f'<b>👁 Статистика дропов в группе /gid{str(group_id).replace("-", "")} [{html.escape(group_info.group_name)}] за сегодня</b>'
                    f'\n\n<b>• Отображение:</b> <code>успешные/в холде/неудачные/повторы/пропуски</code>'
                    f'\n{result}'
                    f'\n\n<b>ℹ️ Тотал:</b> {total_4_1}/{total_4_0}/{total_5}/{total_6}/{total_7}'
                ),
                reply_markup=multi_kb(callback_data='DELETE', text='❌ Закрыть')
            )


    elif action == 'D':
        action = callback_data[2]
        
        async def select_drops_statistics():
            async with get_session() as session:
                status_4_1 = (
                    select(
                        PhoneQueue.drop_id,
                        func.count().label('count_4_1')
                    )
                    .where(
                        PhoneQueue.status == 4,
                        PhoneQueue.waiting_confirm_status == 1
                    )
                    .group_by(PhoneQueue.drop_id)
                    .subquery()
                )

                status_4_0 = (
                    select(
                        PhoneQueue.drop_id,
                        func.count().label('count_4_0')
                    )
                    .where(
                        PhoneQueue.status == 4,
                        PhoneQueue.waiting_confirm_status == 0
                    )
                    .group_by(PhoneQueue.drop_id)
                    .subquery()
                )

                status_5 = (
                    select(
                        PhoneQueue.drop_id,
                        func.count().label('count_5')
                    )
                    .where(PhoneQueue.status == 5)
                    .group_by(PhoneQueue.drop_id)
                    .subquery()
                )

                status_6 = (
                    select(
                        PhoneQueue.drop_id,
                        func.count().label('count_6')
                    )
                    .where(PhoneQueue.status == 6)
                    .group_by(PhoneQueue.drop_id)
                    .subquery()
                )

                status_7 = (
                    select(
                        PhoneQueue.drop_id,
                        func.count().label('count_7')
                    )
                    .where(PhoneQueue.status == 7)
                    .group_by(PhoneQueue.drop_id)
                    .subquery()
                )

                lifetime_subquery = (
                    select(
                        PhoneQueue.drop_id,
                        func.avg(
                            func.extract('epoch', PhoneQueue.slet_at - PhoneQueue.confirmed_at)
                        ).label('avg_lifetime')
                    )
                    .where(
                        PhoneQueue.confirmed_at.isnot(None),
                        PhoneQueue.slet_at.isnot(None)
                    )
                    .group_by(PhoneQueue.drop_id)
                    .subquery()
                )

                users_with_statuses = (
                    select(PhoneQueue.drop_id)
                    .where(PhoneQueue.status.in_([4, 5, 6, 7]))
                    .group_by(PhoneQueue.drop_id)
                    .subquery()
                )

                main_query = (
                    select(
                        User.user_id,
                        User.username,
                        User.fullname,
                        func.coalesce(status_4_1.c.count_4_1, 0).label('success_confirm'),
                        func.coalesce(status_4_0.c.count_4_0, 0).label('success_hold'),
                        func.coalesce(status_5.c.count_5, 0).label('failed'),
                        func.coalesce(status_6.c.count_6, 0).label('repeats'),
                        func.coalesce(status_7.c.count_7, 0).label('skips'),
                        func.coalesce(lifetime_subquery.c.avg_lifetime, 0).label('avg_lifetime')
                    )
                    .select_from(User)
                    .join(users_with_statuses, User.user_id == users_with_statuses.c.drop_id)
                    .outerjoin(status_4_1, User.user_id == status_4_1.c.drop_id)
                    .outerjoin(status_4_0, User.user_id == status_4_0.c.drop_id)
                    .outerjoin(status_5, User.user_id == status_5.c.drop_id)
                    .outerjoin(status_6, User.user_id == status_6.c.drop_id)
                    .outerjoin(status_7, User.user_id == status_7.c.drop_id)
                    .outerjoin(lifetime_subquery, User.user_id == lifetime_subquery.c.drop_id)
                    .where(User.role == 'drop')
                )

                result = await session.execute(main_query)
                stats = result.all()

                formatted_stats = []
                for row in stats:
                    avg_lifetime_seconds = int(row.avg_lifetime) if row.avg_lifetime else 0
                    formatted_lifetime = await format_time(seconds=avg_lifetime_seconds) if avg_lifetime_seconds else '0'
                    
                    user_identifier = f"@{row.username}" if row.username else html.escape(row.fullname)
                    formatted_stats.append([
                        row.user_id,
                        user_identifier,
                        row.success_confirm,
                        row.success_hold,
                        row.failed,
                        row.repeats,
                        row.skips,
                    ])

                return formatted_stats

        if action == 'CSV':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f'temp/drops_statistics_{timestamp}.csv'
            try:
                stats = await select_drops_statistics()
                async with aiofiles.open(file_path, mode='w', newline='', encoding='utf-8') as afp:
                    header = ['ID', 'имя', 'успешные', 'в холде', 'неудачные', 'повторы', 'пропуски']
                    content = [','.join(map(str, row)) for row in ([header] + stats)]
                    await afp.write('\n'.join(content))
                await BotSendDocument(
                    bot,
                    chat_id=callback.from_user.id,
                    document=FSInputFile(file_path),
                    reply_markup=multi_kb(text='✖️', callback_data='DELETE')
                )
            finally:
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error removing file {file_path}: {e}")

        if action == 'M':
            null_status = callback_data[3]
            page = int(callback_data[4])
            writes = await select_users(role='drop', phone_queue_status=True if null_status == 'F' else False)
            total_count_4_1, total_count_4_0, total_count_5, total_count_6, total_count_7= await asyncio.gather(
                select_phone_queues(status=4, waiting_confirm_status=1),
                select_phone_queues(status=4, waiting_confirm_status=0),
                select_phone_queues(status=5),
                select_phone_queues(status=6),
                select_phone_queues(status=7)
            )
            items_per_page = 30
            total_pages = (len(writes) + items_per_page - 1) // items_per_page
            start = (page - 1) * items_per_page
            end = page * items_per_page
            current_writes = writes[start:end]
            result = ''
            for user_info in current_writes:
                count_4_1, count_4_0, count_5, count_6, count_7, lifetime = await asyncio.gather(
                    select_phone_queues(drop_id=user_info.user_id, status=4, waiting_confirm_status=1),
                    select_phone_queues(drop_id=user_info.user_id, status=4, waiting_confirm_status=0),
                    select_phone_queues(drop_id=user_info.user_id, status=5),
                    select_phone_queues(drop_id=user_info.user_id, status=6),
                    select_phone_queues(drop_id=user_info.user_id, status=7),
                    get_qr_codes_average_lifetime(drop_id=user_info.user_id)
                )
                if null_status == 'T' or (null_status == 'F' and (count_4_1 or count_4_0 or count_5 or count_6 or count_7)):
                    result += (
                        f'\n<b>👨‍💻 /uid{user_info.user_id} [{f"@{user_info.username}" if user_info.username else f"<code>{html.escape(user_info.fullname)}</code>"}]:</b> '
                        f'{len(count_4_1)}/{len(count_4_0)}/{len(count_5)}/{len(count_6)}/{len(count_7)}/{lifetime}' 
                    )
            await CallbackEditText(
                callback,
                text=(
                    '<b>👨‍💻 Статистика по дропам</b>'
                    f'\n\n<b>• Отображение:</b> <code>успешные/в холде/неудачные/повторы/пропуски/среднее время жизни</code>'
                    f'\n\n<b>• Просмотр списка с нулём:</b> <code>{"✅ вкл." if null_status == "T" else "❌ выкл."}</code>'
                    f'\n\n<b>ℹ️ Тотал:</b> <code>{len(total_count_4_1)}</code>/<code>{len(total_count_4_0)}</code>/<code>{len(total_count_5)}</code>/<code>{len(total_count_6)}</code>/<code>{len(total_count_7)}</code>'
                    f'\n{result}'
                ),
                reply_markup=await stat_drops_kb(page_action='STAT|D|M', page=page, null_status=null_status, writes=writes, start=start, end=end, total_pages=total_pages)
            )


    elif action == 'P':
        page = int(callback_data[2])
        await CallbackEditText(
            callback,
            text=(
                '<b>📱 Номера в очереди</b>'
                '\n\nВыберите запись:'
            ),
            reply_markup=await stat_phones_queue_kb(page_action='STAT|P', page=page)
        )
    elif action == 'PDEL':
        status = int(callback_data[2])
        if status == 1:
            await CallbackEditText(
                callback,
                text=(
                    '<b>❓ Вы уверены, что хотите удалить все номера из очереди?</b>'
                    ),
                reply_markup=multi_new_2_kb(
                    text='✅ Да', callback_data='STAT|PDEL|2',
                    text2='❌ Нет', callback_data2='STAT|P|1'
                )
            )
        elif status == 2:
            await update_phone_queue(status=0, data={PhoneQueue.status: 15})
            await update_phone_queue(status=12, data={PhoneQueue.status: 15})
            await CallbackAnswer(callback, '🗑 Все номера в очереди были удалены!', show_alert=False)
            await CallbackEditText(
                callback,
                text=(
                    '<b>📱 Номера в очереди</b>'
                    '\n\nВыберите запись:'
                ),
                reply_markup=await stat_phones_queue_kb(page_action='STAT|P', page=1)
            )


    elif action == 'Q':
        page = int(callback_data[2])
        writes = await select_users(role='drop')
        items_per_page = 30
        total_pages = (len(writes) + items_per_page - 1) // items_per_page
        start = (page - 1) * items_per_page
        end = page * items_per_page
        current_writes = writes[start:end]
        result = ''
        for user_info in current_writes:
            result += (
                f'\n<b>👨‍💻 /uid{user_info.user_id} [{f"@{user_info.username}" if user_info.username else f"<code>{html.escape(user_info.fullname)}</code>"}]:</b> '
                f'{len(await select_phone_queues(drop_id=user_info.user_id, status=4))}' 
            )
        await CallbackEditText(
            callback,
            text=(
                '<b>📸 Успешные коды</b>'
                f'\n\n<b>ℹ️ Тотал:</b> {len(await select_phone_queues(status=4))}'
                f'\n{result}'
            ),
            reply_markup=await stat_qrs_queue_kb(page_action='STAT|Q', page=page, writes=writes, start=start, end=end, total_pages=total_pages)
        )


    elif action == 'W':
        page = int(callback_data[2])
        await CallbackEditText(
            callback,
            text=(
                '<b>🛠 Начавшие работу пользователи</b>'
                '\n\nВыберите пользователя:'
            ),
            reply_markup=await stat_users_work_kb(page_action='STAT|W', page=page)
        )


    elif action == 'RESET':
        action = int(callback_data[2])
        if action == 1:
            await CallbackEditText(
                callback,
                text=(
                    '<b>❗️ Вы хотите сбросить статистику?</b>'
                ),
                reply_markup=multi_new_2_kb(
                    text='✅ Да!', callback_data='STAT|RESET|2',
                    text2='❌ Нет', callback_data2='STAT|M',
                )
            )
        elif action == 2:
            await CallbackEditText(
                callback,
                text=(
                    '<b>‼️ Вы уверены, что хотите сбросить статистику?</b>'
                ),
                reply_markup=multi_new_2_kb(
                    text='✅ Да, уверен!', callback_data='STAT|RESET|3',
                    text2='❌ Нет, отмена', callback_data2='STAT|M',
                )
            )
        elif action == 3:
            await CallbackEditText(
                callback,
                text=(
                    '<b>⬇️ Нажмите на кнопку для сброса статистики:</b>'
                ),
                reply_markup=reset_stat_kb()
            )
        elif action == 4:
            await reset_users()
            await reset_phone_queues()
            await CallbackEditText(
                callback,
                text=(
                    '<b>✅ Статистика успешно сброшена!</b>'
                ),
                reply_markup=multi_kb(callback_data='STAT|M')
            )


    elif action == 'C2':
        action = callback_data[2]
        if action == 'M':
            await CallbackEditText(
                callback,
                text=(
                    '<b>💱 Калькулятор дропов</b>'
                    '\n\nВыберите действие:'
                ),
                reply_markup=await calc_kb()
            )

        elif action == 'USD':
            action = callback_data[3]
            if action == 'M':
                main_text = (
                    '<b>💱 Калькулятор дропов • Установка значения</b>'
                    '\n\nВведите число в USD:'
                )
                callback_data_back = 'STAT|C2|M'
                response = await CallbackEditText(callback, text=main_text, reply_markup=multi_new_2_kb(callback_data=callback_data_back))
                await state.set_state(CalcWhatsApp.wait_value)
                await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back)
            elif action == 'L':
                action = callback_data[4]
                value = float(callback_data[5])
                page = int(callback_data[6])
                if action == 'E':
                    user_id = int(callback_data[7])
                    if user_id:
                        await update_user(user_id=user_id, data={User.calc_amount: value})
                    await CallbackAnswer(callback, text=f'✅ {user_id}: {value}$', show_alert=False)
                await CallbackEditText(
                    callback,
                    text=(
                        f'<b>💱 Калькулятор дропов • Установка значения</b>'
                        f'\n\n<b>💲 Новая сумма:</b> {value}'
                        '\n\nВыберите кому вы хотите установить значение:'
                    ),
                    reply_markup=await calc_usd_kb(page_action='STAT|C2|USD|L', page=page, usd=value)
                )

        elif action == 'DS':
            action = callback_data[3]
            if action == 'M':
                await CallbackEditText(
                    callback,
                    text=(
                        '<b>💱 Калькулятор дропов • Объединение дропов</b>'
                        '\n\nВыберите действие:'
                    ),
                    reply_markup=await calc_unification_kb()
                )

            if action == 'C':
                action = callback_data[4]
                unique_id = int(callback_data[5])
                if unique_id == 0:
                    unique_id = int(time.time())
                page = int(callback_data[6])
                if action == 'A':
                    user_id = int(callback_data[7])
                    if not await select_calc_temp(unique_id=unique_id):
                        await add_calc_temp(unique_id=unique_id)
                    if not await select_calc_temp_drop(unique_id=unique_id, user_id=user_id):
                        await add_calc_temp_drop(unique_id=unique_id, user_id=user_id)
                    else:
                        await CallbackAnswer(callback, '❌ Данный дроп уже подключен к объединению!', show_alert=False)
                elif action == 'D':
                    user_id = int(callback_data[7])
                    if await select_calc_temp_drop(unique_id=unique_id, user_id=user_id):
                        await delete_calc_temp_drop(unique_id=unique_id, user_id=user_id)
                    else:
                        await CallbackAnswer(callback, '❌ Данный дроп уже удалён из объединения!', show_alert=False)

                await CallbackEditText(
                    callback,
                    text=(
                        '<b>💱 Калькулятор дропов • Объединение дропов • Создание</b>'
                        f'\n\n<b>🆔 <code>{unique_id}</code></b>'
                        f'\n<b>👥 {len(await select_calc_temp_drops(unique_id=unique_id))}</b>'
                        '\n\nВыберите дропов для объединения в соединение:'
                    ),
                    reply_markup=await calc_unification_create_kb(page_action=f'STAT|C2|DS|C|M|{unique_id}', page=page, unique_id=unique_id)
                )

            if action == 'D':
                action = callback_data[4]
                page = int(callback_data[5])
                if action == 'D':
                    unique_id = int(callback_data[6])
                    if await select_calc_temp(unique_id=unique_id):
                        await delete_calc_temp(unique_id=unique_id)
                        await delete_calc_temp_drop(unique_id=unique_id)
                    else:
                        await CallbackAnswer(callback, '❌ Данное объединение уже удалено!', show_alert=False)
                await CallbackEditText(
                    callback,
                    text=(
                        '<b>💱 Калькулятор дропов • Объединение дропов • Удаление</b>'
                        '\n\nНажмите на кнопку для удаления объединения:'
                    ),
                    reply_markup=await calc_unification_delete_kb(page_action=f'STAT|C2|DS|D|M', page=page)
                )

            if action == 'S':
                action = callback_data[4]
                page = int(callback_data[5])

                if action == 'M':
                    await CallbackEditText(
                        callback,
                        text=(
                            '<b>💱 Калькулятор дропов • Объединение дропов • Редактирование</b>'
                            '\n\nНажмите на кнопку для редактирования объединения:'
                        ),
                        reply_markup=await calc_unification_edit_kb(page_action=f'STAT|C2|DS|S|M', page=page)
                    )
                elif action == 'E':
                    unique_id = int(callback_data[6])
                    action = callback_data[7]
                    page_edit = int(callback_data[8])
                    if not await select_calc_temp(unique_id=unique_id):
                        return await CallbackAnswer(callback, '⚠️ Объединение не найдено! Вернитесь назад к списку')
                    
                    if action == 'A':
                        user_id = int(callback_data[9])
                        await add_calc_temp_drop(unique_id=unique_id, user_id=user_id)
                    elif action == 'D':
                        user_id = int(callback_data[9])
                        await delete_calc_temp_drop(unique_id=unique_id, user_id=user_id)
                    elif action == 'DD':
                        await delete_calc_temp(unique_id=unique_id)
                        await delete_calc_temp_drop(unique_id=unique_id)
                        await CallbackAnswer(callback, '❌ Объединение удалено!', show_alert=True)
                    await CallbackEditText(
                        callback,
                        text=(
                            '<b>💱 Калькулятор дропов • Объединение дропов • Редактирование</b>'
                            f'\n\n<b>🆔 <code>{unique_id}</code></b>'
                            f'\n<b>👥 {len(await select_calc_temp_drops(unique_id=unique_id))}</b>'
                            '\n\nВыберите дропов для объединения в соединение:'
                        ),
                        reply_markup=await calc_unification_edit_menu_kb(page_action=f'STAT|C2|DS|S|E|{page}|{unique_id}|M', page_back_list=page, page=page_edit, unique_id=unique_id)
                    )

        elif action == 'STAT':
            text = ''
            text_connections = ''
            total = 0
            calc_ids = []
            
            calc_writes = await select_calc_temps()
            if calc_writes:
                for calc_write in calc_writes:
                    users = await select_calc_temp_drops(unique_id=calc_write.unique_id)
                    text_drops = ''
                    drops = await asyncio.gather(*(select_user(user_id=user.user_id, auto_withdraw=0) for user in users))
                    valid_drops = [drop for drop in drops if len(await select_phone_queues(drop_id=drop.user_id, status=4, waiting_confirm_status=1, withdraw_status=0)) and drop.calc_amount and drop.calc_amount != 0]
                    for idx, drop in enumerate(valid_drops):
                        count_4 = len(await select_phone_queues(drop_id=drop.user_id, status=4, waiting_confirm_status=1, withdraw_status=0))
                        if count_4 and drop.calc_amount and drop.calc_amount != 0:
                            result = count_4 * float(drop.calc_amount)
                            result = round((result), 6)
                            total += float(result)
                            symbol = '└' if idx == len(valid_drops) - 1 else '├'
                            calc_ids.append(drop.user_id)
                            text_drops += (
                                f'\n<b>{symbol} 👨‍💻 /uid{drop.user_id} [{f"@{drop.username}" if drop.username else f"<code>{html.escape(str(drop.fullname))}</code>"}]:'
                                f' </b>{count_4} * {float(drop.calc_amount)}<b> = {result:.2f} $</b>'
                            )
                    text_connections += f'{text_drops}'

            drops = await select_users(role='drop', auto_withdraw=0)
            if drops:
                for drop in drops:
                    count_4 = len(await select_phone_queues(drop_id=drop.user_id, status=4, waiting_confirm_status=1, withdraw_status=0))
                    if count_4 and drop.calc_amount and drop.calc_amount != 0:
                        if drop.user_id not in calc_ids:
                            result = count_4 * float(drop.calc_amount)
                            result = round((result), 6)
                            total += float(result)
                            text += (
                                f'\n<b>👨‍💻 /uid{drop.user_id} [{f"@{drop.username}" if drop.username else f"<code>{html.escape(str(drop.fullname))}</code>"}]:'
                                f' </b>{count_4} * {float(drop.calc_amount)}<b> = {result:.2f} $</b>'
                            )
            text = (
                '<b>💱 Калькулятор дропов • Просмотр общей статистики</b>'
                '\n<i>🟰 кол-во удачных WA * сохранённое число</i>'
                f'\n\n<b>ℹ️ Тотал:</b> <b>{total:.2f} $</b>'
                f'\n{text}{text_connections}'
            )
            await send_message_parts_4(callback, text)

    elif action == 'GUSD':
        action = callback_data[2]

        if action == 'STAT':
            groups = await select_groups()
            if not groups:
                return await CallbackAnswer(callback, '⚠️ Нет групп для просмотра статистики!', show_alert=True)
            
            total_4_amount = 0
            total_4 = 0
            total_5 = 0
            total_6 = 0
            total_7 = 0
            text = ''
            for group in groups:
                group_id = group.group_id
                _4, _5, _6, _7 = await asyncio.gather(
                    select_phone_queues(group_id=group_id, status=4),
                    select_phone_queues(group_id=group_id, status=5),
                    select_phone_queues(group_id=group_id, status=6),
                    select_phone_queues(group_id=group_id, status=7),
                )
                if _4:
                    _4_amount = len(_4) * group.calc_amount
                    # print(f'_4_amount: {_4_amount}\n\n')
                    _4_amount = round(_4_amount, 6)

                    total_4_amount += _4_amount
                    total_4 += len(_4)
                    total_5 += len(_5)
                    total_6 += len(_6)
                    total_7 += len(_7)
                
                    text += (
                        f'\n<b>👥 /gid{str(group_id).replace("-", "")} [<code>{html.escape(group.group_name)}</code>] (<code>{group.calc_amount}$</code>):</b> '
                        f'{_4_amount}$/{len(_4)}/{len(_5)}/{len(_6)}/{len(_7)}' 
                    )
            text = (
                '<b>💱 Калькулятор групп • Просмотр общей статистики</b>'
                f'\n\n<b>• Отображение:</b> <code>[успешные * сохранённое число/успешные/неудачные/повторы/пропуски] название группы</code>'
                f'\n\n<b>ℹ️ Тотал:</b> {total_4_amount}$/{total_4}/{total_5}/{total_6}/{total_7}' 
                f'\n{text}'
            )
            await send_message_parts_4(callback, text)


        elif action == 'M':
            main_text = (
                'Введите значение в USD:'
            )
            callback_data_back = f'STAT|M'
            response = await CallbackEditText(callback, text=main_text, reply_markup=multi_new_2_kb(callback_data=callback_data_back))
            await state.set_state(SetCalcAmountGroup.wait_value)
            await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back)
        elif action == 'C':
            value = float(callback_data[3])
            page = int(callback_data[4])
            await CallbackEditText(
                callback,
                text=f'<b>💲 Значение:</b> <code>{value}</code>\n\nВыберите куда вы хотите установить данное значение:',
                reply_markup=await set_usd_group_kb(page=page, usd=value)
            )
        elif action == 'S':
            value = float(callback_data[3])
            page = int(callback_data[4])
            group_id = int(callback_data[5])
            await update_group(group_id=group_id, data={Group.calc_amount: value})
            await CallbackAnswer(callback, text=f'✅ {group_id}: {value:.2f}$', show_alert=False)
            await CallbackEditText(
                callback,
                text=f'<b>💲 Значение:</b> <code>{value}</code>\n\nВыберите куда вы хотите установить данное значение:',
                reply_markup=await set_usd_group_kb(page=page, usd=value)
            )
        elif action == 'ALL':
            value = float(callback_data[3])
            page = int(callback_data[4])
            groups = await select_groups()
            if groups:
                for group in groups:
                    await update_group(group_id=group.group_id, data={Group.calc_amount: value})
            await CallbackAnswer(callback, text=f'✅ {value:.2f}$', show_alert=False)
            await CallbackEditText(
                callback,
                text=f'<b>💲 Значение:</b> <code>{value}</code>\n\nВыберите куда вы хотите установить данное значение:',
                reply_markup=await set_usd_group_kb(page=page, usd=value)
            )

@router.message(CalcWhatsApp.wait_value)
async def handler_state(message: Message, bot: Bot, state: FSMContext):
    try:
        state_data = await state.get_data()
        response_message_id = state_data.get('response_message_id')
        main_text = state_data.get('main_text')
        callback_data_back = state_data.get('callback_data_back')
        await state.clear()
        await BotDeleteMessage(bot, chat_id=message.chat.id, message_id=response_message_id)
        value = message.text.strip().lower().replace('$', '').replace(',,', ',').replace('..', '.').replace(',', '.').replace(' ', '')
        if await is_num_calc(value):
            value = float(value)
            return await MessageAnswer(
                message,
                text=(
                    f'<b>💱 Калькулятор дропов • Установка значения</b>'
                    f'\n\n<b>💲 Новая сумма:</b> {value}'
                    '\n\nВыберите кому вы хотите установить значение:'
                ),
                reply_markup=await calc_usd_kb(page_action='STAT|C2|USD|L', page=1, usd=value)
            )
        else:
            await MessageReply(message, f'<b>⚠️ Неверное значение!</b>\n\n<b>❗️ Проверьте введённые данные или попробуйте ещё раз немного позже.</b>')
    except Exception as ex:
        traceback.print_exc()
        await MessageReply(message, f'<b>⚠️ Произошла ошибка при выполнении функции:</b> <code>{str(ex)}</code>')
    response = await MessageAnswer(message, text=main_text, reply_markup=multi_new_2_kb(callback_data=callback_data_back))
    await state.set_state(CalcWhatsApp.wait_value)
    await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back)


@router.message(SetCalcAmountGroup.wait_value)
async def handler_state(message: Message, bot: Bot, state: FSMContext):
    try:
        state_data = await state.get_data()
        response_message_id = state_data.get('response_message_id')
        main_text = state_data.get('main_text')
        callback_data_back = state_data.get('callback_data_back')
        await state.clear()
        await BotDeleteMessage(bot, chat_id=message.chat.id, message_id=response_message_id)
        value = message.text.strip().lower().replace('$', '').replace(',,', ',').replace('..', '.').replace(',', '.').replace(' ', '')
        if await is_num_calc(value):
            value = float(value)
            return await MessageAnswer(
                message,
                text=f'<b>💲 Значение:</b> <code>{value}</code>\n\nВыберите кому вы хотите установить данное значение:',
                reply_markup=await set_usd_group_kb(page=1, usd=value)
            )
        else:
            await MessageReply(message, f'<b>⚠️ Неверное значение!</b>\n\n<b>❗️ Проверьте введённые данные или попробуйте ещё раз немного позже.</b>')
    except Exception as ex:
        traceback.print_exc()
        await MessageReply(message, f'<b>⚠️ Произошла ошибка при выполнении функции:</b> <code>{str(ex)}</code>')
    response = await MessageAnswer(message, text=main_text, reply_markup=multi_new_2_kb(callback_data=callback_data_back))
    await state.set_state(SetCalcAmountGroup.wait_value)
    await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back)

