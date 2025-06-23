from aiogram_imports import *
from common_imports import *
from utils.misc import *

from keyboards.reply.main_kb import *
from keyboards.inline.main_kb import *
from keyboards.inline.misc_kb import *
from keyboards.inline.drop_kb import *


router = Router()
withdraw_locks = defaultdict(asyncio.Lock)
appeal_locks = defaultdict(asyncio.Lock)


@router.callback_query(F.data.startswith('DROP_WORK'))
async def main_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    callback_data = callback.data.split('|')
    action = callback_data[1]
    

    if action == 'MANUAL':
        await update_user(user_id=callback.from_user.id, data={User.manual_read_status: 1})
        us = await select_user(user_id=callback.from_user.id)
        await CallbackMessageAnswer(callback, text='Добро пожаловать!', reply_markup=show_menu_kb)
        return await CallbackEditText(callback, text=await drop_start_text(us=us), reply_markup=await drop_menu_kb(us=us))


    if action == 'START':
        user_info = await select_user(user_id=callback.from_user.id)
        if user_info.unban_at and user_info.unban_at > datetime.now():
            return await CallbackAnswer(
                callback, 
                text=f'⚠️ На ваш аккаунт наложена автоблокировка до {user_info.unban_at.strftime("%d.%m %H:%M")} по МСК.', 
                show_alert=True
            )
        
        await update_user(user_id=callback.from_user.id, data={User.is_work: 1, User.writes_skip_count: 0})
        await update_phone_queue(drop_id=callback.from_user.id, status=12, data={PhoneQueue.status: 0})
        us = await select_user(user_id=callback.from_user.id)
        await CallbackEditText(callback, text=await drop_start_text(us=us), reply_markup=await drop_menu_kb(us=us))


        bt = await select_bot_setting()
        if bt.topic_id and bt.topic_works_theme_id:
            main_bot = await bot_authorization(bot, bot_token=MAIN_BOT_TOKEN)
            if main_bot:
                fullname = f'{callback.from_user.first_name if callback.from_user.first_name is not None else "отсутствует"}{f" {callback.from_user.last_name}" if callback.from_user.last_name is not None else ""}'
                username = f'''<a href="tg://user?id={callback.from_user.id}">{f'@{callback.from_user.username}' if callback.from_user.username is not None else 'отсутствует'}</a>'''
                text = (
                    f'<b>🟢 Начал работу: <a href="https://t.me/{(await main_bot.get_me()).username}?start=u-{callback.from_user.id}">{html.escape(str(fullname))}</a></b>'
                    f'\n• <b>ID:</b> <code>{callback.from_user.id}</code> | <b>US:</b> {username}'
                )
                await BotSendMessage(main_bot, chat_id=bt.topic_id, message_thread_id=bt.topic_works_theme_id, text=text)

    if action == 'STOP':
        await update_user(user_id=callback.from_user.id, data={User.is_work: 0, User.writes_skip_count: 0})
        await update_phone_queue(drop_id=callback.from_user.id, status=0, data={PhoneQueue.status: 12})
        us = await select_user(user_id=callback.from_user.id)
        await CallbackEditText(callback, text=await drop_start_text(us=us), reply_markup=await drop_menu_kb(us=us))

        bt = await select_bot_setting()
        if bt.topic_id and bt.topic_works_theme_id:
            main_bot = await bot_authorization(bot, bot_token=MAIN_BOT_TOKEN)
            if main_bot:
                fullname = f'{callback.from_user.first_name if callback.from_user.first_name is not None else "отсутствует"}{f" {callback.from_user.last_name}" if callback.from_user.last_name is not None else ""}'
                username = f'''<a href="tg://user?id={callback.from_user.id}">{f'@{callback.from_user.username}' if callback.from_user.username is not None else 'отсутствует'}</a>'''
                text = (
                    f'<b>🔴 Закончил работу: <a href="https://t.me/{(await main_bot.get_me()).username}?start=u-{callback.from_user.id}">{html.escape(str(fullname))}</a></b>'
                    f'\n• <b>ID:</b> <code>{callback.from_user.id}</code> | <b>US:</b> {username}'
                )
                await BotSendMessage(main_bot, chat_id=bt.topic_id, message_thread_id=bt.topic_works_theme_id, text=text)


    if action == 'ADD_PHONES':
        bt = await select_bot_setting()
        if bt.added_phones_status == 0:
            return await CallbackAnswer(
                callback, 
                text=(
                    '⚠️ По техническим причинам добавление номеров временно недоступно!'
                    '\n\nПовторите запрос ещё раз немного позже.'
                ), 
                show_alert=True
            )
        user_info = await select_user(user_id=callback.from_user.id)
        await CallbackEditText(
            callback,
            text='<b>Введите номера телефонов РФ, каждую запись указывайте с новой строки:</b>',
            reply_markup=await custom_kb()
        )
        await state.set_state(AddPhones.wait_value)


    if action == 'PQUEUE':
        action = callback_data[2]
        page = int(callback_data[3])
        if action == 'DEL':
            primary_id = int(callback_data[4])
            write = await select_phone_queue(primary_id=primary_id)
            if write and write.status == 0 and write.drop_id == callback.from_user.id:
                user_info = await select_user(user_id=callback.from_user.id)
                await update_phone_queue(primary_id=primary_id, data={PhoneQueue.status: 14})
                await update_user(user_id=callback.from_user.id, data={User.added_count: user_info.added_count - 1 if user_info.added_count >= 1 else 0})
            else:
                await CallbackAnswer(callback, text='⛔️ Данный номер больше нельзя удалить!')
        total_items = await select_many_records(PhoneQueue, count=True, drop_id=callback.from_user.id, status_in=[0,12])
        await CallbackEditText(
            callback,
            text=(
                '<b>⏳ Номера в очереди</b>'
                '\n<i>Нажмите на кнопку, чтобы удалить номер из очереди</i>'
            ),
            reply_markup=await get_added_phones(
                user_id=callback.from_user.id, 
                total_items=total_items, 
                page=page
            )
        )


    if action == 'P':
        found_text = ''
        action = callback_data[2]

        if action == 'I':
            await CallbackEditText(
                callback, 
                text=(
                    '<b>Выберите нужный раздел:</b>'
                    f'\n<i>По умолчанию показаны записи за неделю</i>'
                ), 
                reply_markup=await drop_archive_menu_kb(user_id=callback.from_user.id)
            )

        elif action == 'N':
            action = callback_data[3]
            if action == 'M':
                period = callback_data[4]
                page = int(callback_data[5])
                total_items = await select_many_records(PhoneQueue, count=True, drop_id=callback.from_user.id, added_at=period)
                
                # if not total_items:
                #     return await CallbackAnswer(
                #         callback, 
                #         text=f'✖️ У вас нет номеров за {await get_time_at_period(period)}', 
                #         show_alert=True
                #     )
                if total_items:
                    found_text = f'\n\n<b>→ Найдено записей:</b> <code>{total_items}</code>'
                await CallbackEditText(
                    callback,
                    text=(
                        f'<b>📁 Архив номеров за {await get_time_at_period(period)}</b>'
                        '\n<i>Нажмите на кнопку, чтобы получить подробную информацию о записи</i>'
                        f'{found_text}'
                    ),
                    reply_markup=await get_drop_list_phones_kb(
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
                    return await CallbackAnswer(callback,  text='❓ Номер не найден', show_alert=True)
                if write.drop_id != callback.from_user.id:
                    return await CallbackAnswer(callback,  text='🔒 Вы не можете просматривать информацию по данному номеру.', show_alert=True)
                text = await get_write_info_for_drop(write)
                reply_markup = await custom_v2_kb(
                    text='Закрыть', callback_data='DELETE',
                    text2='Обновить', callback_data2=f'DROP_WORK|P|N|O|U|{write.id}',
                )
                if action == 'V':
                    await CallbackMessageAnswer(callback, text=text, reply_markup=reply_markup)
                if action == 'U':
                    await CallbackEditText(callback, text=text, reply_markup=reply_markup)

        elif action == 'C':
            action = callback_data[3]
            if action == 'M':
                period = callback_data[4]
                page = int(callback_data[5])
                total_items = await select_many_records(PhoneQueue, count=True, drop_id=callback.from_user.id, slet_at=period, check_id_is_not_none=True)
                
                # if not total_items:
                #     return await CallbackAnswer(
                #         callback, 
                #         text=f'✖️ У вас нет чеков за {await get_time_at_period(period)}', 
                #         show_alert=True
                #     )
                
                items_per_page = 12
                offset = (page - 1) * items_per_page
                total_pages = (total_items + items_per_page - 1) // items_per_page
                writes = await select_many_records(
                    PhoneQueue,
                    drop_id=callback.from_user.id, 
                    sort_desc='slet_at', 
                    slet_at=period,
                    check_id_is_not_none=True,
                    limit=items_per_page,
                    offset=offset,
                )
                text = ''
                if writes:
                    found_text = f'\n\n<b>→ Найдено записей:</b> <code>{total_items}</code>'
                    for write in writes:
                        text += (
                            f'\n<b>→ <code>{write.phone_number}</code> • <a href="http://t.me/send?start={write.check_id}">{write.check_id}</a>'
                            f'{f" • <code>{write.calc_amount - write.referrer_calc_amount}$</code>" if write.calc_amount > 0 and write.referrer_calc_amount is not None else ""}</b>'
                        )
                else:
                    text += f'\n<i>У вас нет чеков за {await get_time_at_period(period)}</i>'
                await CallbackEditText(
                    callback,
                    text=(
                        f'<b>📁 Архив чеков</b>'
                        '\n<i>Нажмите на встроенную ссылку, чтобы активировать чек, если он ещё не использован</i>'
                        f'{found_text}'
                        f'\n{text}'
                    ),
                    reply_markup=await get_drop_list_checks_kb(
                        period=period,
                        total_pages=total_pages,
                        page=page
                    )
                )
                

        elif action == 'W':
            action = callback_data[3]
            if action == 'M':
                period = callback_data[4]
                page = int(callback_data[5])
                total_items = await select_many_records(Withdraw, count=True, user_id=callback.from_user.id, created_at=period)
                
                # if not total_items:
                #     return await CallbackAnswer(
                #         callback, 
                #         text=f'✖️ У вас нет выводов за {await get_time_at_period(period)}', 
                #         show_alert=True
                #     )
                
                items_per_page = 12
                offset = (page - 1) * items_per_page
                total_pages = (total_items + items_per_page - 1) // items_per_page
                writes = await select_many_records(
                    Withdraw,
                    user_id=callback.from_user.id, 
                    created_at=period,
                    sort_desc='created_at', 
                    limit=items_per_page,
                    offset=offset
                )
                text = ''
                if writes:
                    found_text = f'\n\n<b>→ Найдено записей:</b> <code>{total_items}</code>'
                    for write in writes:
                        text += (
                            f'\n<b>→ {await get_withdraw_status_emoji(write.withdraw_status)} {await get_withdraw_status(write.withdraw_status)}:'
                            f' <code>{write.created_at.strftime("%d.%m.%Y %H:%M")}</code>'
                            f'''{f' • <a href="http://t.me/send?start={write.check_id}">{write.check_id}</a>' if write.check_id else ''}'''
                            f'{f" • <code>{write.amount}$</code>" if write.amount else ""}</b>'
                        )
                else:
                    text += f'\n<i>У вас нет выводов за {await get_time_at_period(period)}</i>'

                await CallbackEditText(
                    callback,
                    text=(
                        f'<b>📁 Архив выводов</b>'
                        '\n<i>Нажмите на встроенную ссылку, чтобы активировать чек, если он ещё не использован</i>'
                        f'{found_text}'
                        f'\n{text}'
                    ),
                    reply_markup=await get_drop_list_withdraws_kb(
                        period=period,
                        total_pages=total_pages,
                        page=page
                    )
                )


    if action == 'STAT':
        hold_query = select_phone_queues(drop_id=callback.from_user.id, status=4, waiting_confirm_status=0)
        confirmed_query = select_phone_queues(drop_id=callback.from_user.id, status=4, waiting_confirm_status=1)
        failed_query = select_phone_queues(drop_id=callback.from_user.id, status=5)
        repeated_query = select_phone_queues(drop_id=callback.from_user.id, status=6)
        missed_query = select_phone_queues(drop_id=callback.from_user.id, status=7)
        
        in_progress_statuses = [1, 2, 3]
        limit_query = select_phone_queues(drop_id=callback.from_user.id, statuses=[0] + in_progress_statuses)
        queue_query = select_phone_queues(drop_id=callback.from_user.id, status=0)
        processing_query = select_phone_queues(drop_id=callback.from_user.id, statuses=in_progress_statuses)
        total_queue_query = select_phone_queues(status=0)
        total_processing_query = select_phone_queues(statuses=in_progress_statuses)
        
        results = await asyncio.gather(
            select_user(user_id=callback.from_user.id),
            select_bot_setting(),
            hold_query, confirmed_query, failed_query, 
            repeated_query, missed_query, limit_query,
            queue_query, processing_query,
            total_queue_query, total_processing_query
        )
        
        user_info, bot_settings = results[0], results[1]
        hold_count, confirmed_count, failed_count = len(results[2]), len(results[3]), len(results[4])
        repeated_count, missed_count, limit_count = len(results[5]), len(results[6]), len(results[7])
        queue_count, processing_count = len(results[8]), len(results[9])
        total_queue_count, total_processing_count = len(results[10]), len(results[11])

        await CallbackEditText(
            callback,
            text=(
                '<b>📊 Статистика за сегодня</b>'
                f'\n├ <b>В холде:</b> <code>{hold_count}</code>'
                f'\n├ <b>Засчитано:</b> <code>{confirmed_count}</code>'
                f'\n├ <b>Слётов:</b> <code>{failed_count}</code>'
                f'\n├ <b>Повторов:</b> <code>{repeated_count}</code>'
                f'\n├ <b>Пропущено:</b> <code>{missed_count}</code>'
                f'\n└ <b>Добавлено:</b> <code>{user_info.added_count}</code>'

                '\n\n<b>ℹ️ Номера</b>'
                f'\n├ <b>Ваш лимит:</b> <code>{limit_count}</code>/<code>{bot_settings.limit_wa}</code>'
                f'\n├ <b>В очереди:</b> <code>{queue_count}</code>'
                f'\n├ <b>В обработке:</b> <code>{processing_count}</code>'
                f'\n├ <b>Всего в очереди:</b> <code>{total_queue_count}</code>'
                f'\n└ <b>Всего в обработке:</b> <code>{total_processing_count}</code>'
            ),
            reply_markup=await update_v2_kb(callback_data='DROP_WORK|STAT')
        )


    if action == 'Y':
        primary_id = callback_data[2]
        write = await select_phone_queue(primary_id=primary_id)
        if write and (write.status == 3 or write.status == 18) and write.drop_id == callback.from_user.id:
            if write.status == 3:
                await update_phone_queue(
                    primary_id=write.id,
                    data={
                        PhoneQueue.status: 4,
                        PhoneQueue.confirmed_at: datetime.now(),
                        PhoneQueue.updated_at: datetime.now(),
                    }
                )
            elif write.status == 18:
                await update_phone_queue(
                    primary_id=write.id,
                    data={
                        PhoneQueue.appeal_status: 1,
                        PhoneQueue.status: 4,
                        PhoneQueue.slet_at: None,
                        PhoneQueue.updated_at: datetime.now(),
                    }
                )
            await update_user(user_id=write.drop_id, data={User.writes_skip_count: 0})
            text = f'<b>✅ Подтверждён:</b> <code>{write.phone_number}</code>'
            await CallbackEditCaption(callback, caption=text, reply_markup=None)
            response = await BotSendMessage(
                await bot_authorization(bot, bot_id=write.group_bot_id), 
                chat_id=write.group_id, 
                reply_to_message_id=write.group_user_message_id, 
                text=text, 
                reply_markup=await custom_2_kb(
                    text='❌', callback_data=f'QUEUE|SLET|{write.id}',
                    text2='⚠️ Не установлен', callback_data2=f'QUEUE|ERROR|{write.id}|0'
                )
            )
            if response:
                await update_phone_queue(
                    primary_id=write.id,
                    data={
                        PhoneQueue.group_bot_message_id: response.message_id,
                    }
                )
        else:
            await CallbackEditCaption(
                callback,
                caption=f'<b>⛔️ Запись недействительна:</b> <code>{write.phone_number}</code>',
                reply_markup=None
            )


    if action == 'N':
        primary_id = callback_data[2]
        write = await select_phone_queue(primary_id=primary_id)
        if write and (write.status == 3 or write.status == 18) and write.drop_id == callback.from_user.id:
            if write.status == 3:
                if (write.skip_count + 1) >= 2:
                    await update_phone_queue(
                        primary_id=write.id,
                        data={
                            PhoneQueue.status: 6,
                            PhoneQueue.updated_at: datetime.now(),
                            PhoneQueue.skip_count: PhoneQueue.skip_count + 1
                        }
                    )
                    await update_user(user_id=write.drop_id, data={User.writes_skip_count: 0})
                    await CallbackEditCaption(
                        callback, 
                        caption=f'<b>❌ Номер удалён из-за постоянных пропусков:</b> <code>{write.phone_number}</code>', 
                        reply_markup=None
                    )
                    await BotSendMessage(
                        await bot_authorization(bot, bot_id=write.group_bot_id), 
                        chat_id=write.group_id, 
                        reply_to_message_id=write.group_user_message_id, 
                        text=f'<b>🚫 WhatsApp под номером <code>{write.phone_number}</code> не удалось связать. Возьмите новый номер по команде /nomer</b>'
                    )
                else:
                    await update_phone_queue(
                        primary_id=write.id,
                        data={
                            PhoneQueue.status: 2,
                            PhoneQueue.updated_at: datetime.now(),
                            PhoneQueue.skip_count: PhoneQueue.skip_count + 1
                        }
                    )
                    await update_user(user_id=write.drop_id, data={User.writes_skip_count: 0})
                    await CallbackEditCaption(
                        callback, 
                        caption=f'<b>❌ Отменён:</b> <code>{write.phone_number}</code>', 
                        reply_markup=None
                    )
                    text = (
                        f'<b>❌ Не удалось связать WhatsApp <code>{write.phone_number}</code>, пришлите ответом на сообщение новый код.</b>'
                        '\n\n<b>❗️ У вас есть две минуты для ответа!</b>'
                        f'<a href="tg://sql?write_id={write.id}">\u2063</a>'
                    )
                    response = await BotSendMessage(
                        await bot_authorization(bot, bot_id=write.group_bot_id), 
                        chat_id=write.group_id, 
                        reply_to_message_id=write.group_user_message_id, 
                        text=text
                    )
                    if response:
                        await update_phone_queue(
                            primary_id=write.id,
                            data={
                                PhoneQueue.group_bot_message_id: response.message_id,
                            }
                        )

            elif write.status == 18:
                await update_phone_queue(
                    primary_id=write.id,
                    data={
                        PhoneQueue.status: 5,
                        PhoneQueue.updated_at: datetime.now(),
                    }
                )
                await update_user(user_id=write.drop_id, data={User.writes_skip_count: 0})
                await CallbackEditCaption(
                    callback,
                    caption=f'<b>❌ Слёт:</b> <code>{write.phone_number}</code>',
                    reply_markup=None
                )
                await BotSendMessage(
                    await bot_authorization(bot, bot_id=write.group_bot_id), 
                    chat_id=write.group_id, 
                    reply_to_message_id=write.group_user_message_id, 
                    text=f'<b>🚫 WhatsApp под номером <code>{write.phone_number}</code> не удалось связать. Возьмите новый номер по команде /nomer</b>'
                )
        else:
            await CallbackEditCaption(
                callback,
                caption=f'<b>⛔️ Запись недействительна:</b> <code>{write.phone_number}</code>',
                reply_markup=None
            )


    if action == 'APPEAL':
        primary_id = int(callback_data[2])
        async with appeal_locks[primary_id]:
            write = await select_phone_queue(primary_id=primary_id)
            if not write:
                await CallbackEditText(callback, text=str(callback.message.html_text), reply_markup=None)
                return await CallbackAnswer(callback, text='❌ Запись не найдена!', show_alert=True)
            if write.drop_id != callback.from_user.id:
                await CallbackEditText(callback, text=str(callback.message.html_text), reply_markup=None)
                return await CallbackAnswer(callback, text='❌ Данная запись не принадлежит вам!', show_alert=True)
            if write.status != 5 or write.appeal_status != 0 or write.admin_appeal_confirm_status != 0:
                await CallbackEditText(callback, text=str(callback.message.html_text), reply_markup=None)
                return await CallbackAnswer(callback, text='❌ Данную запись больше нельзя обжаловать!', show_alert=True)
            if await different_time(write.slet_at, 3):
                await CallbackEditText(callback, text=str(callback.message.html_text), reply_markup=None)
                return await CallbackAnswer(callback, text='❌ Данную запись больше нельзя обжаловать!', show_alert=True)
            bt = await select_bot_setting()
            if bt.topic_id and bt.topic_slet_applications_theme_id and bt.topic_slet_applications_theme_id != 0:
                main_bot = await bot_authorization(bot, bot_token=MAIN_BOT_TOKEN)
                if main_bot:
                    await update_phone_queue(primary_id=primary_id, data={PhoneQueue.appeal_status: 1})
                    fullname = f'{callback.from_user.first_name if callback.from_user.first_name is not None else "отсутствует"}{f" {callback.from_user.last_name}" if callback.from_user.last_name is not None else ""}'
                    username = f'''<a href="tg://user?id={callback.from_user.id}">{f'@{callback.from_user.username}' if callback.from_user.username is not None else 'отсутствует'}</a>'''
                    text = (
                            f'<b>⁉️ <a href="https://t.me/{(await main_bot.get_me()).username}?start=u-{callback.from_user.id}">{html.escape(str(fullname))}</a> просит обжаловать слёт</b>'
                            f'\n\n• <b>ID:</b> <code>{callback.from_user.id}</code> | <b>US:</b> {username}'
                            f'\n\n{await get_qr_code_info(write)}'
                        )
                    reply_markup = await custom_2_kb(
                        text='✅ Принять', callback_data=f'APPEAL|YES|{primary_id}',
                        text2='❌ Отклонить', callback_data2=f'APPEAL|NO|{primary_id}',
                    )
                    await BotSendMessage(main_bot, chat_id=bt.topic_id, message_thread_id=bt.topic_slet_applications_theme_id, text=text, reply_markup=reply_markup)
                    await CallbackEditText(callback, text=str(callback.message.html_text), reply_markup=None)
            else:
                return await CallbackAnswer(callback, text='⚠️ На данный момент данную запись нельзя обжаловать! Повторите попытку ещё раз немного позже.', show_alert=True)


    if action == 'REF':
        action = callback_data[2]
        if action == 'M':
            user, bot_settings, today_refs, yesterday_refs, week_refs, month_refs, all_refs, active_refs, total_withdraws = await asyncio.gather(
                select_user(user_id=callback.from_user.id),
                select_bot_setting(),
                select_users(referrer_id=callback.from_user.id, period_registered_at="today"),
                select_users(referrer_id=callback.from_user.id, period_registered_at="yesterday"),
                select_users(referrer_id=callback.from_user.id, period_registered_at="start_week"),
                select_users(referrer_id=callback.from_user.id, period_registered_at="start_month"),
                select_users(referrer_id=callback.from_user.id),
                select_users(referrer_id=callback.from_user.id, role="drop", is_banned=0),
                get_total_withdraws_amount(user_id=callback.from_user.id)
            )

            if not user.user_hash:
                user_hash = await generate_random_code()
                await update_user(user_id=callback.from_user.id, data={User.user_hash: user_hash})
                user = await select_user(user_id=callback.from_user.id)

            if user.part_referral_amount_max <= 0:
                await update_user(user_id=callback.from_user.id, data={User.part_referral_amount_max: bot_settings.drop_ref_max})
                user = await select_user(user_id=callback.from_user.id)

            await CallbackEditText(
                callback,
                text=(
                    '<b>🤝 Реферальная программа</b>'
                    f'\n<i>Получайте фиксированную сумму с поставленных номеров вашего реферала.</i>'

                    f'\n\n<b>🆔 Ваш ID:</b> <code>{callback.from_user.id}</code>'

                    f'\n\n<b>📊 Регистрации</b>'
                    f'\n├ <b>За сегодня:</b> <code>{len(today_refs)}</code>'
                    f'\n├ <b>За вчера:</b> <code>{len(yesterday_refs)}</code>'
                    f'\n├ <b>С начала недели:</b> <code>{len(week_refs)}</code>'
                    f'\n├ <b>С начала месяца:</b> <code>{len(month_refs)}</code>'
                    f'\n└ <b>За всё время:</b> <code>{len(all_refs)}</code>'

                    f'\n\n<b>🧑‍💻 Активных рефералов:</b> <code>{len(active_refs)}</code>'

                    f'\n\n<b>💸 Вы получаете <code>{user.part_referral_amount}$</code> из <code>{user.part_referral_amount_max}$</code> за номер</b>'
                    
                    f'\n\n<b>💵 Всего заработано:</b> <code>{famount(total_withdraws + user.ref_balance)}$</code>'
                    f'\n<b>💳 Доступно к выводу:</b> <code>{famount(user.ref_balance)}$</code>'

                    '\n\n<b>🔗 Ссылка для приглашений:</b>'
                    f'\n→ <code>https://t.me/{(await bot.get_me()).username}?start={user.user_hash}</code>'
                    
                    '\n\n<b>🆕 Создайте своё зеркало бота и расширьте возможности:</b>'
                    f'\n→ Каждый новый пользователь зеркала перешедший не по ссылке — автоматически становится вашим рефералом'
                ),
                reply_markup=await ref_menu_kb(user_id=callback.from_user.id)
            )


        elif action == 'EDIT':
            us = await select_user(user_id=callback.from_user.id)
            action = callback_data[3]
            if action == 'E':
                new_part_referral_amount = int(callback_data[4])
                if new_part_referral_amount > us.part_referral_amount_max:
                    await CallbackAnswer(callback, f'⚠️ Вы не можете установить значение больше вашей максимальной ставки ({us.part_referral_amount_max})!', show_alert=True)
                else:
                    await update_user(user_id=callback.from_user.id, data={User.part_referral_amount: new_part_referral_amount})
            us = await select_user(user_id=callback.from_user.id)
            await CallbackEditText(
                callback,
                text=(
                    f'<b>Ваша ставка:</b> <code>{us.part_referral_amount}$</code>'
                    f'\n<b>Максимальная ставка:</b> <code>{us.part_referral_amount_max}$</code>'
                    '\n\n<b>Выберите какую суммую вы хотите получать с каждого поставленного номера рефералом:</b>'
                ),
                reply_markup=await ref_choice_kb(current_amount=us.part_referral_amount, max_amount=us.part_referral_amount_max)
            )

        elif action == 'WITHDRAW':
            us = await select_user(user_id=callback.from_user.id)
            action = callback_data[3]
            min_amount_withdraw = 10
            if us.ref_balance >= min_amount_withdraw:
                if action == 'M':
                    await CallbackEditText(
                        callback,
                        text=(
                            f'<b>💳 Доступно к выводу:</b> <code>{famount(us.ref_balance)}$</code>'
                            '\n\n<b>Выберите сумму на которую вы хотите создать чек:</b>'
                        ),
                        reply_markup=await ref_withdraw_kb(ref_balance=us.ref_balance)
                    )
                if action == 'C':
                    amount = float(callback_data[4])
                    if us.ref_balance >= amount:
                        await CallbackEditText(
                            callback,
                            text=(
                                '<b>Для создания заявки требуется подтверждение:</b>'
                            ),
                            reply_markup=await custom_2_kb(
                                text=f'✅ Вывести {amount}$', callback_data=f'DROP_WORK|REF|WITHDRAW|W|{amount}',
                                text2='Изменить сумму', callback_data2=f'DROP_WORK|REF|WITHDRAW|M',
                            )
                        )
                    else:
                        await CallbackAnswer(callback, f'У вас недостаточный баланс для вывода выбранной суммы!', show_alert=True)

                if action == 'W':
                    amount = float(callback_data[4])
                    async with withdraw_locks[callback.from_user.id]:
                        us = await select_user(user_id=callback.from_user.id)
                        if us.ref_balance >= amount:
                            await update_user(user_id=callback.from_user.id, data={User.ref_balance: User.ref_balance - amount})
                            await add_withdraw(
                                user_id=callback.from_user.id,
                                amount=amount
                            )
                            await CallbackEditText(
                                callback,
                                text=(
                                    f'<b>✔️ Заявка на вывод <code>{famount(amount)}$</code> успешно создана!</b>'
                                    '\n<i>В ближайшее время вам придёт чек криптобота.</i>'
                                )
                            )
                        else:
                            await CallbackAnswer(callback, f'У вас недостаточный баланс для вывода выбранной суммы!', show_alert=True)
            else:
                await CallbackAnswer(callback, f'Минимальная сумма для вывода: {min_amount_withdraw}$\nВаш баланс: {famount(us.ref_balance)}$', show_alert=True)


@router.callback_query(F.data.startswith('BOTS'))
async def main_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    callback_data = callback.data.split('|')
    action = callback_data[1]

    if action == 'RULES':
        await CallbackEditText(
            callback,
            text=(
                '<b>❌ Запрещается:</b>'

                '\n\n<b>1. Создание зеркальных ботов с использованием неприемлемых описаний, названий или изображений:</b>'
                '\n   — 🚫 Оскорбительные или провокационные тексты.'
                '\n   — 🚫 Неуместные, аморальные или шокирующие фото и аватары.'
                '\n   — 🚫 Использование клеветы, угроз или оскорблений в любом виде.'
                '\n   — 🚫 Любые материалы сексуального характера (включая текст, изображения, видео и прочее).'

                '\n\n<b>2. Использование ботов для распространения:</b>'
                '\n   — 🔥 Разжигания вражды, дискриминации или любых форм ненависти.'
                '\n   — 📩 Спама, мошенничества или обмана.'

                '\n\n<b>3. Любые проявления грубости, унижения или угроз в описаниях, названиях, аватарах:</b>'
                '\n   — 😡 Оскорбления, уничижительные выражения.'
                '\n   — 🚫 Контент сексуального характера или непристойности.'

                '\n\n<b>⚠️ Важно:</b>'
                '\n   — ⛔️ Нарушение этих правил приведёт к немедленной блокировке бота или вашего аккаунта.'
                '\n   — 💰 Все заработанные средства с нарушающего бота могут быть заморожены или аннулированы.'
            ),
            reply_markup=await custom_kb(callback_data='BOTS|CREATE')
        )

    if action == 'CREATE':
        await CallbackEditText(
            callback,
            text=(
                '<b>Шаг 1: Войдите в @BotFather</b>'
                '\nВам необходимо открыть приложение Telegram и в строке поиска ввести @BotFather. BotFather - это официальный бот, созданный разработчиками Telegram, чтобы помочь пользователям создавать их собственные боты.'

                '\n\n<b>Шаг 2: Нажмите кнопку Начать или Start</b>'
                '\nВ нижней части экрана вы увидите кнопку Начать. По нажатию на нее BotFather отправит вам сообщение с приветствием и списком доступных команд.'

                '\n\n<b>Шаг 3: Введите команду /newbot</b>'
                '\nВ ответ на приветственное сообщение BotFather нужно отправить команду /newbot. Это сообщит BotFather, что вы хотите создать нового бота.'

                '\n\n<b>Шаг 4: Введите имя бота</b>'
                '\nBotFather попросит вас ввести имя для вашего нового бота. Это имя будет отображаться пользователям Telegram при взаимодействии с вашим ботом.'

                '\n\n<b>Шаг 5: Введите уникальное имя бота</b>'
                '\nПосле того как вы ввели имя, BotFather попросит вас выбрать уникальное имя пользователя для вашего бота. Это имя должно быть уникальным и заканчиваться на bot. Если выбранный вами никнейм уже занят, BotFather попросит вас выбрать другое имя.'

                '\n\n<b>Шаг 6: Вы получите токен бота</b>'
                '\nПосле успешного создания бота BotFather отправит вам сообщение с токеном вашего бота. Этот токен необходим вам для программирования функционала бота и его подключения к API Telegram.'

                '\n\n<b>Шаг 7: Скопируйте полученный токен и отправьте его сюда</b>'
            ),
            reply_markup=await create_bot_kb()
        )

    if action == 'MY':
        action = callback_data[2]

        if action == 'M':
            sort_type = int(callback_data[3])
            page = int(callback_data[4])
            await CallbackEditText(
                callback,
                text=(
                    '<b>Здесь вы можете видеть список всех Ваших зеркал</b>'
                    '\n<i>Для редактирования или просмотра информации о боте выберите его ниже</i>'
                ),
                reply_markup=await my_bots_kb(page=page, user_id=callback.from_user.id, current_bot_id=bot.id, sort_type=sort_type)
            )

        elif action == 'V':
            sort_type = int(callback_data[3])
            back_page = int(callback_data[4])
            bot_id = int(callback_data[5])
            action = callback_data[6]

            bot_info = await select_one_record(BotBase, owner_id=callback.from_user.id, bot_id=bot_id)
            if not bot_info:
                return await CallbackAnswer(callback, text='❌ Бот недоступен.', show_alert=True)
            if bot_info.owner_id != callback.from_user.id:
                return await CallbackAnswer(callback, text='❌ Данный бот не привязан к вашему аккаунту.', show_alert=True)
            if bot_info.is_deleted:
                return await CallbackAnswer(callback, text='❌ Бот удалён.', show_alert=True)
            if bot_info.is_deleted or bot_info.is_unauthorized:
                return await CallbackAnswer(callback, text='❌ Слетел токен авторизации.', show_alert=True)

            if action == 'M':
                page_action = f'BOTS|MY|V|{sort_type}|{back_page}|{bot_id}'
                await CallbackEditText(
                    callback,
                    text=await user_get_bot_info(bot_info),
                    reply_markup=await view_bot_kb(page_action=page_action, sort_type=sort_type, back_page=back_page)
                )
                    
            elif action == 'DL':
                bot_settings = {"session": bot.session}
                new_bot = Bot(
                    token=bot_info.bot_token,
                    **bot_settings
                )
                try:
                    bot_user = await new_bot.get_me()
                    await new_bot.delete_webhook()
                except TelegramUnauthorizedError:
                    await update_record(
                        BotBase, 
                        bot_token=bot_info.bot_token, 
                        data={
                            BotBase.is_unauthorized: True
                        }
                    )
                except:
                    try:
                        await new_bot.delete_webhook()
                    except:
                        pass
                    traceback.print_exc()
                await update_record(
                    BotBase, 
                    bot_token=bot_info.bot_token, 
                    data={
                        BotBase.is_deleted: True,
                    }
                )
                page_action = f'BOTS|MY|V|{sort_type}|{back_page}|{bot_id}'
                await CallbackEditText(
                    callback,
                    text=f'<b>🚫 БОТ УДАЛЁН</b>\n\n{await user_get_bot_info(bot_info)}',
                    reply_markup=await view_bot_kb(page_action=page_action, sort_type=sort_type, back_page=back_page)
                )


@router.message(AddPhones.wait_value)
async def state_AddPhones(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    user_info = await select_user(user_id=message.from_user.id)
    limit_wa = (await select_bot_setting()).limit_wa
    bt = await select_bot_setting()
    if bt.added_phones_status == 0:
        return await MessageReply(message, f'<b>⚠️ По техническим причинам приём номеров временно недоступен, повторите добавление ещё раз немного позже!</b>')
    if user_info.unban_at and user_info.unban_at > datetime.now():
        return await MessageReply(message, f'<b>⚠️ Вы не можете выполнить это действие! На ваш аккаунт наложена автоблокировка до {user_info.unban_at.strftime("%d.%m.%Y %H:%M")}</b>')
    else:
        list_phones = [] # с повторами
        not_recognized = 0
        count_writes = 0
        count_added = 0
        already_added = 0
        already_processing = 0
        not_valid_operator = 0
        # already_success = 0
        queue_limit = 0
        try:
            msg_text = message.text.strip().split('\n')
        except:
            msg_text = None
        if not msg_text:
            return
        if not msg_text:
            msg_text = ['123']
        for phone in msg_text:
            count_writes += 1
            phone = phone.replace('+', '').replace('(', '').replace(')', '').replace('-', '').replace(' ', '').replace('/', '').replace('\\', '').replace('—', '')
            if not phone or not phone.isdigit():
                not_recognized += 1
                continue
            if len(phone) == 11 and phone[0] == '7' and phone[1] == '9':
                list_phones.append(phone[1:])
            elif len(phone) == 11 and phone[0] == '8' and phone[1] == '9':
                list_phones.append(phone[1:])
            elif len(phone) == 10 and phone[0] == '9':
                list_phones.append(phone)
            else:
                not_recognized += 1

        true_phones = list(set(list_phones)) # без повторов
        count_duplicates = len(list_phones) - len(true_phones) # дубликаты
        for number in true_phones:
            add_status = False

            if bt.phone_operator_check_status and not await validate_russian_phone(phone=number):
                not_valid_operator += 1
                continue

            if await select_phone_queue(phone_number=number, statuses=[0, 12]):
                already_added += 1 # уже добавлен
            # elif count_added >= limit_wa:
            #     queue_limit += 1 # лимит очереди
            elif await select_phone_queue(phone_number=number, statuses=[1, 2, 3]):
                already_processing += 1 # в статусе обработки
            elif len(await select_phone_queues(drop_id=message.from_user.id, statuses=[0, 1, 2, 3, 12])) >= limit_wa:
                queue_limit += 1 # лимит очереди
            else:
                count_added += 1 # добавлен
                add_status = True
            if add_status:
                await add_phone_queue(drop_id=message.from_user.id, phone_number=number, drop_bot_id=bot.id)
                await update_user(user_id=message.from_user.id, data={User.added_count: User.added_count + 1})
        await MessageAnswer(
            message,
            text=(
                f'<b>✅ Добавлено:</b> {count_added}/{count_writes}'
                + (f"\n\n<b>ℹ️ Детали проверки номеров:</b>" if count_added != count_writes else "")
                + (f"\n• <b>Повторов:</b> {count_duplicates}" if count_duplicates else "")
                + (f"\n• <b>Уже в очереди:</b> {already_added}" if already_added else "")
                + (f"\n• <b>Уже в работе:</b> {already_processing}" if already_processing else "")
                + (f"\n• <b>Не удалось распознать:</b> {not_recognized}" if not_recognized else "")
                + (f"\n• <b>Неверный формат или оператор:</b> {not_valid_operator}" if not_valid_operator else "")
                + (f"\n• <b>Превышен лимит номеров в очереди:</b> {queue_limit} ({len(await select_phone_queues(drop_id=message.from_user.id, statuses=[0, 1, 2, 3, 12]))}/{limit_wa})" if queue_limit else "")
                + (f'\n\n<b>📊 Статистика:</b>')
                + (f'\n• <b>Всего номеров в очереди:</b> {len(await select_phone_queues(status=0))}')
                + (f'\n• <b>Ваших номеров в очереди:</b> {len(await select_phone_queues(drop_id=message.from_user.id, status=0))}')
                + (f'\n• <b>Ваших номеров в обработке:</b> {len(await select_phone_queues(drop_id=message.from_user.id, statuses=[1, 2, 3]))}')
                + (f'\n\n<b>⬇️ Введите новый список номеров или вернитесь в главное меню:</b>')
            ),
            reply_markup=await custom_kb()
        )
        await state.set_state(AddPhones.wait_value)


@router.message()
async def message_handler(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    try:
        msg = message.text.strip()
        message_text = msg.replace(' ', '')
    except:
        message_text = None
    if not message_text:
        return
    
    is_token = await is_bot_token(message_text)
    if is_token:
        bot_settings = {"session": bot.session}
        new_bot = Bot(
            token=message_text,
            **bot_settings
        )
        try:
            bot_user = await new_bot.get_me()
        except TelegramUnauthorizedError:
            if await select_one_record(BotBase, bot_token=message_text):
                await update_record(
                    BotBase, 
                    bot_token=message_text, 
                    data={
                        BotBase.owner_id: message.from_user.id,
                        BotBase.is_unauthorized: True
                    }
                )

            return await MessageAnswer(message, text="<b>⛔️ Неверно задан api-ключ!</b>\n<i>Пришлите новый токен или перевыпустите текущий.</i>")
        
        if await select_one_record(BotBase, bot_token=message_text):
            # await new_bot.delete_webhook()
            await new_bot.set_webhook(url=OTHER_BOTS_URL.format(bot_token=message_text), allowed_updates=allowed_updates)
            await update_record(
                BotBase, 
                    bot_token=message_text, 
                data={
                    BotBase.owner_id: message.from_user.id,
                    BotBase.bot_name: bot_user.first_name, 
                    BotBase.bot_username: bot_user.username,
                    BotBase.is_deleted: False,
                    BotBase.is_unauthorized: False
                }
            )
            return await MessageAnswer(
                message, 
                text=f"<b>❕ Бот @{bot_user.username} уже подключен к системе, выберите действие:</b>",
                reply_markup=await custom_kb(text="⚙️ Перейти к просмотру", callback_data=f"BOTS|MY|V|0|1|{bot_user.id}|M")
            )
        else:
            if await select_one_record(BotBase, bot_id=bot_user.id):
                await update_record(
                    BotBase, 
                    bot_id=bot_user.id, 
                    data={
                        BotBase.owner_id: message.from_user.id,
                        BotBase.bot_name: bot_user.first_name, 
                        BotBase.bot_username: bot_user.username,
                        BotBase.bot_token: message_text, 
                        BotBase.is_deleted: False,
                        BotBase.is_unauthorized: False
                    }
                )
            else:
                await add_record(
                    BotBase,
                    owner_id=message.from_user.id, 
                    bot_id=bot_user.id,
                    bot_name=bot_user.first_name,
                    bot_username=bot_user.username,
                    bot_token=message_text,
                    added_at=datetime.now(),
                    updated_at=datetime.now(),
                )
        await new_bot.delete_webhook()
        await new_bot.set_webhook(url=OTHER_BOTS_URL.format(bot_token=message_text), allowed_updates=allowed_updates)
        await MessageAnswer(
            message, 
            text=f"<b>✅ Бот @{bot_user.username} успешно подключен к системе.</b>",
            reply_markup=await custom_kb(text="⚙️ Перейти к просмотру", callback_data=f"BOTS|MY|V|0|1|{bot_user.id}|M")
        )
        await set_default_commands(bot=new_bot)
        try:
            await asyncio.wait_for(upload_profile_photo(bot_token=message_text), timeout=60)
        except asyncio.TimeoutError:
            pass
        except:
            traceback.print_exc()
        return
    else:
        us = await select_user(user_id=message.from_user.id)
        await MessageAnswer(message, text='Добро пожаловать!', reply_markup=show_menu_kb)
        await MessageAnswer(message, text=await drop_start_text(us=us), reply_markup=await drop_menu_kb(us=us))