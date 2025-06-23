from aiogram import Bot, Router, F, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from utils.additionally_bot import *

from keyboards.reply.main_kb import *
from keyboards.inline.main_kb import *
from keyboards.inline.misc_kb import *
from keyboards.inline.manager_kb import *
from keyboards.inline.application import admin_application_kb, admin_application_ban_kb

from database.tables import User, Application
from database.commands.main import *
from database.commands.users import *
from database.commands.applications import *
from database.commands.bot_settings import *

from states.main_modules import *

from utils.misc import *

router = Router()
topic_commands_locks = defaultdict(asyncio.Lock)



@router.callback_query(F.data.startswith('TOPIC_US'))
async def my_applications_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    callback_data = callback.data.split('|')
    primary_id = int(callback_data[1])
    ban_status = callback_data[2]
    write = await select_phone_queue(primary_id=primary_id)
    await update_user(user_id=write.drop_id, data={User.is_banned: 1 if ban_status == 'BAN' else 0})
    if ban_status == 'BAN':
        await update_record(PhoneQueue, drop_id=write.drop_id, unban_month_status=0, status=18, slet_at_is_not_none=True, data={PhoneQueue.pslet_status: 1})
        await update_record(PhoneQueue, drop_id=write.drop_id, unban_month_status=0, status_in=[23,24], slet_at_is_not_none=True, data={PhoneQueue.pslet_status: 1})
        # await update_record(PhoneQueue, drop_id=write.drop_id, confirmed_status=1, withdraw_status=0, pre_withdraw_status_in=[0,1], data={PhoneQueue.pre_withdraw_status: 4}) # аннулирование баланса
    await CallbackEditText(
        callback, 
        text=await get_nevalid_session_info(user_info=await select_user(user_id=write.drop_id), write=write),
        reply_markup=multi_2_kb(
            text='🚷 Заблокировать', callback_data=f'TOPIC_US|{write.id}|BAN', 
            text_back='☑️ Разблокировать', callback_data_back=f'TOPIC_US|{write.id}|UNBAN', 
        ),
        disable_web_page_preview=True
    )

@router.callback_query(F.data.startswith('APPL'))
async def my_applications_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    callback_data = callback.data.split('|')
    action = callback_data[1]
    application_id = callback_data[2]
    application_info = await select_application(primary_id=application_id)
    if action == 'YES':
        bt = await select_bot_setting()
        await update_user(user_id=application_info.user_id, data={User.role: 'drop', User.calc_amount: bt.main_drop_calc_amount})
        await update_application(primary_id=application_id, data={Application.application_status: 1})
        text = str(callback.message.html_text).replace(' <b>запрашивает доступ к функционалу</b>', '').replace('🔔 ', '\n<b>├ Пользователь: </b>')
        await CallbackEditText(callback=callback, text='<b>✅ Заявка одобрена!</b>' + text, reply_markup=await multi_new_2_kb(text='💲 Установить значение', callback_data=f'MNG|U|L|V|1|USD|{application_info.user_id}|1', text2='❌ Закрыть', callback_data2='DELETE'), disable_web_page_preview=True)
        await BotSendMessage(bot=bot, chat_id=application_info.user_id, text=f'<b>✅ Ваша заявка была одобрена!</b>\n\nПропишите /start для обновления меню.')
    elif action == 'NO':
        await update_application(primary_id=application_id, data={Application.application_status: 2})
        text = str(callback.message.html_text).replace(' <b>запрашивает доступ к функционалу</b>', '').replace('🔔 ', '\n<b>├ Пользователь: </b>')
        await CallbackEditText(callback=callback, text='<b>❌ Заявка отклонена!</b>' + text, reply_markup=multi_kb('DELETE', '❌ Закрыть'), disable_web_page_preview=True)
        await BotSendMessage(bot=bot, chat_id=application_info.user_id, text=f'<b>❌ Ваша заявка была отклонена!</b>')
    elif action == 'BAN':
        notification_status = callback_data[3]
        await update_user(user_id=application_info.user_id, data={User.is_banned: 1})
        await update_application(primary_id=application_id, data={Application.application_status: 2})
        text = str(callback.message.html_text).replace(' <b>запрашивает доступ к функционалу</b>', '').replace('🔔 ', '\n<b>├ Пользователь: </b>').replace(' без уведомления', '').replace('<b>✅ Пользователь был разблокирован!</b>', '').replace('<b>🚫 Пользователь был заблокирован!</b>', '')
        await CallbackEditText(callback=callback, text=f'<b>🚫 Пользователь был заблокирован{" без уведомления" if notification_status == "1" else ""}!</b>' + text, reply_markup=admin_application_ban_kb(application_id, '✅ Разбанить', 'UNBAN'), disable_web_page_preview=True)
        if notification_status == '0':
            await BotSendMessage(bot=bot, chat_id=application_info.user_id, text=f'<b>🚫 Вам был ограничен доступ к боту!</b>')
    elif action == 'UNBAN':
        notification_status = callback_data[3]
        await update_user(user_id=application_info.user_id, data={User.is_banned: 0})
        text = str(callback.message.html_text).replace(' <b>запрашивает доступ к функционалу</b>', '').replace('🔔 ', '\n<b>├ Пользователь: </b>').replace(' без уведомления', '').replace('<b>✅ Пользователь был разблокирован!</b>', '').replace('<b>🚫 Пользователь был заблокирован!</b>', '')
        await CallbackEditText(callback=callback, text=f'<b>✅ Пользователь был разблокирован{" без уведомления" if notification_status == "1" else ""}!</b>' + text, reply_markup=admin_application_ban_kb(application_id, '🚫 Забанить', 'BAN'), disable_web_page_preview=True)
        if notification_status == '0':
            await BotSendMessage(bot=bot, chat_id=application_info.user_id, text=f'<b>✅ Вам был восстановлен доступ к боту!</b>')


@router.callback_query(F.data.startswith('MNG'))
async def callback_query(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    callback_data = callback.data.split('|')
    action = callback_data[1]

    if action == 'U':
        action = callback_data[2]
        if action == 'M':
            await CallbackEditText(
                callback,
                text=(
                    '<b>👤 Управление пользователями</b>'
                    '\n\nВыберите действие:'
                ),
                reply_markup=manage_users()
            )

        elif action == 'SEARCH':
            main_text = (
                '<b>👤 Управление пользователями • Поиск</b>'
                '\n\nВведите ID пользователя:'
            )
            callback_data_back = 'MNG|U|M'
            response = await CallbackEditText(callback, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
            await state.set_state(UserIdSearch.wait_value)
            await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back)

        elif action == 'L':
            action = callback_data[3]
            page = int(callback_data[4])

            if action == 'M':
                await CallbackEditText(
                    callback,
                    text=(
                        '<b>👤 Управление пользователями • Список</b>'
                        '\n\nВыберите пользователя:'
                    ),
                    reply_markup=await users_list(page=page)
                )

            elif action == 'G':
                user_id = int(callback_data[5])
                write = await select_user(user_id=user_id)
                await CallbackMessageAnswer(
                    callback,
                    text=await get_user_info(write),
                    reply_markup=await user_manage_kb(write=write, page=page)
                )

            elif action == 'V':
                action = callback_data[5]
                user_id = int(callback_data[6])
                write = await select_user(user_id=user_id)
                if not write:
                    return await CallbackAnswer(callback, text='⚠️ Пользователь не найден!', show_alert=True)

                if action == 'W':
                    value = int(callback_data[7])
                    if value == 1:
                        await update_phone_queue(drop_id=user_id, status=12, data={PhoneQueue.status: 0})
                    elif value == 0:
                        await update_phone_queue(drop_id=user_id, status=0, data={PhoneQueue.status: 12})
                    await update_user(user_id=user_id, data={User.is_work: value})
                elif action == 'B':
                    value = int(callback_data[7])
                    if value == 0:
                        await update_user(user_id=user_id, data={User.is_banned: value, User.auto_ban_status: 0})
                    elif value == 1:
                        await update_user(user_id=user_id, data={User.is_banned: value})
                        await update_record(PhoneQueue, drop_id=user_id, unban_month_status=0, status=18, slet_at_is_not_none=True, data={PhoneQueue.pslet_status: 1})
                        await update_record(PhoneQueue, drop_id=user_id, unban_month_status=0, status_in=[23,24], slet_at_is_not_none=True, data={PhoneQueue.pslet_status: 1})
                        # await update_record(PhoneQueue, drop_id=user_id, confirmed_status=1, withdraw_status=0, pre_withdraw_status_in=[0,1], data={PhoneQueue.pre_withdraw_status: 4}) # аннулирование баланса
                                        
                    if value == 1:
                        await kick_user(bot, user_id)
                elif action == 'AWS':
                    value = int(callback_data[7])
                    await update_user(user_id=user_id, data={User.auto_withdraw_status: value})
                elif action == 'CLEAR_A_B_C':
                    await update_user(user_id=user_id, data={User.auto_ban_count: 0})
                elif action == 'R':
                    value = str(callback_data[7])
                    await update_user(user_id=user_id, data={User.role: value})
                    if value == 'client':
                        await kick_user(bot, user_id)
                elif action == 'CLEAR_LOCK':
                    await update_user(user_id=user_id, data={User.phones_added_ban_expired_at: None})
                elif action == 'RCB':
                    await update_user(user_id=user_id, data={User.ban_count: 0, User.unban_at: datetime.now() - timedelta(minutes=1)})
                elif action == 'LIMIT':
                    await update_user(user_id=user_id, data={User.added_count: 0})
                elif action == 'P':
                    await CallbackEditText(
                        callback,
                        text=f'<b>📁 Все записи пользователя <code>{user_id}</code></b>',
                        reply_markup=await user_phones_queue_kb(user_id=user_id, page=int(callback_data[7]), page_list=page)
                    )
                elif action == 'Q':
                    await CallbackEditText(
                        callback,
                        text=f'<b>📸 Коды пользователя <code>{user_id}</code> за сегодня</b>',
                        reply_markup=await user_qrs_queue_kb(user_id=user_id, page=int(callback_data[7]), page_list=page)
                    )
                elif action == 'AW':
                    value = int(callback_data[7])
                    await update_user(user_id=user_id, data={User.auto_withdraw: value})

                elif action == 'USD':
                    status = int(callback_data[7])
                    main_text = (
                        f'{await get_user_info_2(write)}'
                        '\n\nВведите новое значение в USD:'
                    )
                    callback_data_back = f'MNG|U|L|V|{page}|U|{write.user_id}'
                    if status == 0:
                        response = await CallbackEditText(callback, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
                    else:
                        response = await CallbackMessageAnswer(callback, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
                        # response = await BotSendMessage(bot, chat_id=callback.from_user.id, text=main_text, reply_markup=multi_new_2_kb(callback_data=callback_data_back))
                    await state.set_state(EditUserCalcAmount.wait_value)
                    await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back, user_id=write.user_id)
                
                elif action == 'PERCENT':
                    status = int(callback_data[7])
                    main_text = (
                        f'{await get_user_info_2(write)}'
                        '\n\nВведите новое значение процентной ставки по рефке (например <code>2.5</code>) для пользователя:'
                    )
                    callback_data_back = f'MNG|U|L|V|{page}|U|{write.user_id}'
                    if status == 0:
                        response = await CallbackEditText(callback, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
                    else:
                        response = await CallbackMessageAnswer(callback, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
                    await state.set_state(EditUserRefPercent.wait_value)
                    await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back, user_id=write.user_id)
                
                elif action == 'BALANCE':
                    status = int(callback_data[7])
                    main_text = (
                        f'{await get_user_info_2(write)}'
                        '\n\nВведите новый баланс пользователя:'
                    )
                    callback_data_back = f'MNG|U|L|V|{page}|U|{write.user_id}'
                    if status == 0:
                        response = await CallbackEditText(callback, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
                    else:
                        response = await CallbackMessageAnswer(callback, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
                    await state.set_state(EditUserBalance.wait_value)
                    await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back, user_id=write.user_id)
                
                elif action == 'REF_BALANCE':
                    status = int(callback_data[7])
                    main_text = (
                        f'{await get_user_info_2(write)}'
                        '\n\nВведите новый баланс партнёрского счёта пользователя:'
                    )
                    callback_data_back = f'MNG|U|L|V|{page}|U|{write.user_id}'
                    if status == 0:
                        response = await CallbackEditText(callback, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
                    else:
                        response = await CallbackMessageAnswer(callback, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
                    await state.set_state(EditUserRefBalance.wait_value)
                    await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back, user_id=write.user_id)

                if action not in ['P', 'Q', 'USD', 'PERCENT', 'BALANCE', 'REF_BALANCE']:
                    write = await select_user(user_id=user_id)
                    await CallbackEditText(
                        callback,
                        text=await get_user_info(write),
                        reply_markup=await user_manage_kb(write=write, page=page)
                    )


    elif action == 'G':
        action = callback_data[2]
        if action == 'M':
            await CallbackEditText(
                callback,
                text=(
                    '<b>👥 Управление группами</b>'
                    '\n\n<b>ℹ️ Команды для взаимодействия внутри группы:</b>'
                    '\n<b>├ Добаить:</b> <code>/gadd</code>'
                    '\n<b>└ Удалить:</b> <code>/gdel</code>'
                    '\n\nВыберите действие:'
                ),
                reply_markup=manage_groups()
            )

        elif action == 'ADD':
            main_text = (
                '<b>➕ Управление группами • Добавить по ID</b>'
                '\n\nВведите один или несколько ID групп (до 50 за сообщение):'
            )
            callback_data_back = 'MNG|G|M'
            response = await CallbackEditText(callback, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
            await state.set_state(AddGroupByID.wait_value)
            await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back)

        elif action == 'DEL':
            main_text = (
                '<b>➖ Управление группами • Удалить из базы по ID</b>'
                '\n\n<b>❗️ Данная функция полностью удаляет группу из базы!</b>'
                '\n\nВведите один или несколько ID групп (до 50 за сообщение):'
            )
            callback_data_back = 'MNG|G|M'
            response = await CallbackEditText(callback, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
            await state.set_state(DeleteGroupByID.wait_value)
            await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back)

        elif action == 'S':
            action = callback_data[3]
            page = int(callback_data[4])

            if action == 'T':
                group_id = int(callback_data[5])
                work_status = int(callback_data[6])
                await update_group(group_id=group_id, data={Group.work_status: work_status})
                await CallbackAnswer(callback, text=f'{"✅ Группа включена!" if work_status == 1 else "❌ Группа выключена!"}', show_alert=False)
            elif action == 'AT':
                work_status = int(callback_data[5])
                await update_group(data={Group.work_status: work_status})
                await CallbackAnswer(callback, text=f'{"✅ Все группы включены!" if work_status == 1 else "❌ Все группы выключены!"}', show_alert=False)

            if action == 'E':
                action = callback_data[5]
                group_id = int(callback_data[6])
                group_info = await select_group(group_id=group_id)
                if not group_info:
                    return await CallbackAnswer(callback, text='⚠️ Не удалось найти группу!', show_alert=True)
                    
                if action == 'T':
                    work_status = int(callback_data[7])
                    await update_group(group_id=group_id, data={Group.work_status: work_status})
                    await CallbackAnswer(callback, text=f'{"✅ Группа включена!" if work_status == 1 else "❌ Группа выключена!"}', show_alert=False)
                elif action == 'D':
                    await delete_group(group_id=group_id)
                    await CallbackAnswer(callback, text='❌ Группа удалена!', show_alert=True)
        
                elif action == 'OTL':
                    action = callback_data[7]
                    pg = int(callback_data[8])
                    if action == 'E':
                        unique_id = int(callback_data[9])
                        status = callback_data[10]
                        if status == 'A':
                            if await select_one_record(OtlegaGroup, unique_id=unique_id) or unique_id == 111:
                                if not await select_one_record(OtlegaGroupBase, unique_id=unique_id, group_id=group_id):
                                    await add_record(OtlegaGroupBase, unique_id=unique_id, group_id=group_id, added_at=datetime.now())
                        elif status == 'D':
                            await delete_record(OtlegaGroupBase, unique_id=unique_id, group_id=group_id)

                    return await CallbackEditText(
                        callback,
                        text=(
                            f'<b>🕒 Подключение подгрупп на группу <code>{group_id}</code></b>'
                            '\n\nНажмите на кнопку чтобы включить или отключить выдачу подгруппы:'
                        ),
                        reply_markup=await groups_otl_kb(group_id=group_id, page=pg)
                    )
                

                if action != 'D':
                    group_info = await select_group(group_id=group_id)
                    await CallbackEditText(
                        callback,
                        text=await get_group_info(group_info=group_info),
                        reply_markup=await group_manage_kb(write=group_info, page=page),
                        disable_web_page_preview=True
                    )
            else:
                await CallbackEditText(
                    callback,
                    text='<b>⚙️ Управление группами • Настройки</b>'
                    '\n\n<b>Обозначения:</b>'
                    '\n✅ — включить группу'
                    '\n❌ — отключить группу'
                    '\n\nНажмите на кнопку чтобы включить или отключить группу:',
                    reply_markup=await groups_settings(page=page)
                )


@router.message(EditUserCalcAmount.wait_value)
async def handler_state(message: Message, bot: Bot, state: FSMContext):
    try:
        state_data = await state.get_data()
        response_message_id = state_data.get('response_message_id')
        main_text = state_data.get('main_text')
        callback_data_back = state_data.get('callback_data_back')
        user_id = state_data.get('user_id')
        await state.clear()
        await BotDeleteMessage(bot, chat_id=message.chat.id, message_id=response_message_id)
        value = message.text.strip().lower().replace('$', '').replace(',,', ',').replace('..', '.').replace(',', '.').replace(' ', '')
        if user_id and await is_num_calc(value):
            value = float(value)
            await update_user(user_id=user_id, data={User.calc_amount: value})
            write = await select_user(user_id=user_id)
            return await MessageAnswer(
                message,
                text=await get_user_info(write),
                reply_markup=await user_manage_kb(write=write, page=1)
            )
        else:
            await MessageReply(message, f'<b>⚠️ Неверное значение!</b>\n\n<b>❗️ Проверьте введённые данные или попробуйте ещё раз немного позже.</b>')
    except Exception as ex:
        traceback.print_exc()
        await MessageReply(message, f'<b>⚠️ Произошла ошибка при выполнении функции:</b> <code>{str(ex)}</code>')
    response = await MessageAnswer(message, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
    await state.set_state(EditUserCalcAmount.wait_value)
    await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back, user_id=user_id)

@router.message(EditUserRefPercent.wait_value)
async def handler_state(message: Message, bot: Bot, state: FSMContext):
    try:
        state_data = await state.get_data()
        response_message_id = state_data.get('response_message_id')
        main_text = state_data.get('main_text')
        callback_data_back = state_data.get('callback_data_back')
        user_id = state_data.get('user_id')
        await state.clear()
        await BotDeleteMessage(bot, chat_id=message.chat.id, message_id=response_message_id)
        value = message.text.strip().lower().replace('%', '').replace('$', '').replace(',,', ',').replace('..', '.').replace(',', '.').replace(' ', '')
        if user_id and await is_num_calc(value):
            value = float(value)
            await update_user(user_id=user_id, data={User.ref_percent: value})
            write = await select_user(user_id=user_id)
            return await MessageAnswer(
                message,
                text=await get_user_info(write),
                reply_markup=await user_manage_kb(write=write, page=1)
            )
        else:
            await MessageReply(message, f'<b>⚠️ Неверное значение!</b>\n\n<b>❗️ Проверьте введённые данные или попробуйте ещё раз немного позже.</b>')
    except Exception as ex:
        traceback.print_exc()
        await MessageReply(message, f'<b>⚠️ Произошла ошибка при выполнении функции:</b> <code>{str(ex)}</code>')
    response = await MessageAnswer(message, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
    await state.set_state(EditUserRefPercent.wait_value)
    await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back, user_id=user_id)

@router.message(EditUserBalance.wait_value)
async def handler_state(message: Message, bot: Bot, state: FSMContext):
    try:
        state_data = await state.get_data()
        response_message_id = state_data.get('response_message_id')
        main_text = state_data.get('main_text')
        callback_data_back = state_data.get('callback_data_back')
        user_id = state_data.get('user_id')
        await state.clear()
        await BotDeleteMessage(bot, chat_id=message.chat.id, message_id=response_message_id)
        value = message.text.strip().lower().replace('%', '').replace('$', '').replace(',,', ',').replace('..', '.').replace(',', '.').replace(' ', '')
        if user_id and await is_num_calc(value):
            value = float(value)
            await update_user(user_id=user_id, data={User.balance: value})
            write = await select_user(user_id=user_id)
            return await MessageAnswer(
                message,
                text=await get_user_info(write),
                reply_markup=await user_manage_kb(write=write, page=1)
            )
        else:
            await MessageReply(message, f'<b>⚠️ Неверное значение!</b>\n\n<b>❗️ Проверьте введённые данные или попробуйте ещё раз немного позже.</b>')
    except Exception as ex:
        traceback.print_exc()
        await MessageReply(message, f'<b>⚠️ Произошла ошибка при выполнении функции:</b> <code>{str(ex)}</code>')
    response = await MessageAnswer(message, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
    await state.set_state(EditUserBalance.wait_value)
    await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back, user_id=user_id)

@router.message(EditUserRefBalance.wait_value)
async def handler_state(message: Message, bot: Bot, state: FSMContext):
    try:
        state_data = await state.get_data()
        response_message_id = state_data.get('response_message_id')
        main_text = state_data.get('main_text')
        callback_data_back = state_data.get('callback_data_back')
        user_id = state_data.get('user_id')
        await state.clear()
        await BotDeleteMessage(bot, chat_id=message.chat.id, message_id=response_message_id)
        value = message.text.strip().lower().replace('%', '').replace('$', '').replace(',,', ',').replace('..', '.').replace(',', '.').replace(' ', '')
        if user_id and await is_num_calc(value):
            value = float(value)
            await update_user(user_id=user_id, data={User.ref_balance: value})
            write = await select_user(user_id=user_id)
            return await MessageAnswer(
                message,
                text=await get_user_info(write),
                reply_markup=await user_manage_kb(write=write, page=1)
            )
        else:
            await MessageReply(message, f'<b>⚠️ Неверное значение!</b>\n\n<b>❗️ Проверьте введённые данные или попробуйте ещё раз немного позже.</b>')
    except Exception as ex:
        traceback.print_exc()
        await MessageReply(message, f'<b>⚠️ Произошла ошибка при выполнении функции:</b> <code>{str(ex)}</code>')
    response = await MessageAnswer(message, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
    await state.set_state(EditUserRefBalance.wait_value)
    await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back, user_id=user_id)


@router.message(UserIdSearch.wait_value)
async def handler_state(message: Message, bot: Bot, state: FSMContext):
    try:
        state_data = await state.get_data()
        response_message_id = state_data.get('response_message_id')
        main_text = state_data.get('main_text')
        callback_data_back = state_data.get('callback_data_back')
        await state.clear()
        await BotDeleteMessage(bot, chat_id=message.chat.id, message_id=response_message_id)

        user_id = message.text.strip().lower().replace('#id', '').replace('/uid', '').replace('/u', '').replace(' ', '')
        try:
            user_id = int(user_id)
        except:
            user_id = None
        if user_id and str(user_id).isdigit():
            write = await select_user(user_id=user_id)
            if not write:
                await MessageReply(message, f'<b>⚠️ Пользователь не найден.</b>\n\n<b>❗️ Проверьте введённые данные или попробуйте ещё раз немного позже.</b>')
            else:
                return await MessageAnswer(
                    message,
                    text=await get_user_info(write),
                    reply_markup=await user_manage_kb(write=write, page=1)
                )
        else:
            await MessageReply(message, f'<b>⚠️ Неверное значение!</b>\n\n<b>❗️ Проверьте введённые данные или попробуйте ещё раз немного позже.</b>')
    except Exception as ex:
        traceback.print_exc()
        await MessageReply(message, f'<b>⚠️ Произошла ошибка при выполнении функции:</b> <code>{str(ex)}</code>')
    response = await MessageAnswer(message, text=main_text, reply_markup=await multi_new_2_kb(callback_data=callback_data_back))
    await state.set_state(UserIdSearch.wait_value)
    await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back)




@router.message()
async def message_handler(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    sent_message = message.text.strip().replace(' ', '').lower()
    if sent_message.startswith('/uid') or sent_message.startswith('/u'):
        await BotDeleteMessage(bot, chat_id=message.chat.id, message_id=message.message_id)
        user_id = message.text.strip().lower().replace('#id', '').replace('/uid', '').replace('/u', '')
        if user_id.isdigit():
            user_info = await select_user(user_id=user_id)
            if user_info:
                await MessageAnswer(
                    message,
                    text=await get_user_info(user_info),
                    reply_markup=await user_manage_kb(write=user_info, page=1)
                )
            else:
                await MessageAnswer(
                    message=message,
                    text='<b>❌ Пользователь не найден!</b>\n\nВведите ID без лишиних символов или вернитесь в главное меню:',
                    reply_markup=multi_kb()
                )
        else:
            await MessageAnswer(
                message=message,
                text='<b>❌ Не удалось распознать ID пользователя!</b>\n\nВведите ID без лишиних символов или вернитесь в главное меню:',
                reply_markup=multi_kb()
            )
        await state.set_state(ManageUser.wait_value)
    elif sent_message.startswith('/gid') or sent_message.startswith('/g'):
        await BotDeleteMessage(bot, chat_id=message.chat.id, message_id=message.message_id)
        group_id = message.text.strip().lower().replace('#id', '').replace('/gid', '').replace('/g', '').replace('-', '')
        if group_id.isdigit():
            group_id = int(f'-{group_id}')
            group_info = await select_group(group_id=group_id)
            if group_info:
                await MessageAnswer(
                    message,
                    text=await get_group_info(group_info),
                    reply_markup=await group_manage_kb(write=group_info, page=1),
                    disable_web_page_preview=True
                )
            else:
                await MessageAnswer(
                    message=message,
                    text='<b>❌ Группа не найдена!</b>',
                    reply_markup=multi_kb()
                )
        else:
            await MessageAnswer(
                message=message,
                text='<b>❌ Не удалось распознать ID группы!</b>',
                reply_markup=multi_kb()
            )

