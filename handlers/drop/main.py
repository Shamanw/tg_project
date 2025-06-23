import re

from aiogram import Bot, Router, F, html
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from keyboards.reply.main_kb import *
from keyboards.inline.main_kb import *
from keyboards.inline.misc_kb import *
from keyboards.inline.drop_kb import *

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
user_record_locks = defaultdict(asyncio.Lock)
user_record_locks2 = defaultdict(asyncio.Lock)


@router.callback_query(F.data.startswith('DROP_WORK'))
async def main_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    callback_data = callback.data.split('|')
    action = callback_data[1]
    
    user_info = await select_user(user_id=callback.from_user.id)
    if user_info and not user_info.is_banned:
        if action == 'MANUAL':
            await update_user(user_id=callback.from_user.id, data={User.manual_read_status: 1})
            await CallbackMessageAnswer(callback, text='\u2063', reply_markup=show_menu_kb)
            await BotSendMessage(
                bot=bot,
                chat_id=callback.from_user.id,
                text='Выберите действие:',
                reply_markup=drop_menu_kb()
            )

        elif action == 'OTMENA':
            primary_id = int(callback_data[2])
            write = await select_phone_queue(primary_id=primary_id)
            if not write:
                return await CallbackAnswer(callback, text='🚫 Запись не найдена!', show_alert=True)
            if write.status != 1:
                return await CallbackAnswer(callback, text='🚫 Авторизацию больше нельзя отменить!', show_alert=True)
            await update_phone_queue(primary_id=primary_id, data={PhoneQueue.status: 25})
            await CallbackEditText(
                callback,
                text=(
                    f'<b>❌ Отмена авторизации:</b> <code>{write.phone_number}</code>'
                ),
                reply_markup=None
            )

        elif action == 'ADD_PHONES':
            if user_info.phones_added_ban_expired_at and user_info.phones_added_ban_expired_at > datetime.now():
                return await CallbackAnswer(callback, text=f'⚠️ Вы не можете добавлять новые номера до {user_info.phones_added_ban_expired_at.strftime("%d.%m %H:%M")}', show_alert=True)
            bt = await select_bot_setting()
            if bt.added_phones_status == 0:
                return await CallbackAnswer(callback, text='🚫 На данный момент приём новых номеров в боте выключен, попробуйте ещё раз немного позже.', show_alert=True)
            elif bt.day_count_sended >= bt.day_limit_sended:
                return await CallbackAnswer(callback, text='🚫 Достигнут дневной лимит вбитых номеров в боте, попробуйте ещё раз немного позже.', show_alert=True)
            elif bt.day_count_added >= bt.day_limit_added:
                return await CallbackAnswer(callback, text='🚫 Достигнут дневной лимит добавленных номеров в боте, попробуйте ещё раз немного позже.', show_alert=True)
            await CallbackEditText(
                callback,
                text=f'Введите до 10 номеров телефонов РФ для добавления аккаунтов:',
                reply_markup=multi_kb()
            )
            await state.set_state(AddPhones.wait_value)

        elif action == 'STAT':
            bt = await select_bot_setting()
            await CallbackEditText(
                callback,
                text=(
                    '\n\n<b>☀️ За сегодня:</b>'
                    f'\n<b>├ Оплаченных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, set_at="today", set_at_is_not_none=True, alive_status_not_in=[1,2,3])}</code>'
                    f'\n<b>├ Выданных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, alive_hold_status=0, status=17, buyed_at="today", buyed_at_is_not_none=True)}</code>'
                    f'\n<b>├ Слетевших:</b> <code>{(await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status=18, slet_main_at="today", slet_main_at_is_not_none=True)) + (await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status=17, alive_status_in=[1,2,3], slet_main_at="today", slet_main_at_is_not_none=True)) + (await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, alive_status_not_in=[1,2,3], alive_hold_status=1, status=17, buyed_at="today"))}</code> '
                    f'\n<b>├ Невалидных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status_in=[23,24], slet_main_at="today", slet_main_at_is_not_none=True)}</code>'
                    f'\n<b>├ Замороженных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status=42, slet_main_at="today", slet_main_at_is_not_none=True)}</code>'
                    f'\n<b>└ Разблокированных:</b> <code>{await select_many_records(PhoneQueue, count=True, unban_month_status=1, drop_id=user_info.user_id, unlocked_at="today", unlocked_at_is_not_none=True)}</code>'

                    '\n\n<b>🌑 За вчера:</b>'
                    f'\n<b>├ Оплаченных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, set_at="yesterday", set_at_is_not_none=True, alive_status_not_in=[1,2,3])}</code>'
                    f'\n<b>├ Выданных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, alive_hold_status=0, status=17, buyed_at="yesterday", buyed_at_is_not_none=True)}</code>'
                    f'\n<b>├ Слетевших:</b> <code>{(await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status=18, slet_main_at="yesterday", slet_main_at_is_not_none=True)) + (await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status=17, alive_status_in=[1,2,3], slet_main_at="yesterday", slet_main_at_is_not_none=True)) + (await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, alive_status_not_in=[1,2,3], alive_hold_status=1, status=17, buyed_at="yesterday"))}</code> '
                    f'\n<b>├ Невалидных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status_in=[23,24], slet_main_at="yesterday", slet_main_at_is_not_none=True)}</code>'
                    f'\n<b>├ Замороженных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status=42, slet_main_at="yesterday", slet_main_at_is_not_none=True)}</code>'
                    f'\n<b>└ Разблокированных:</b> <code>{await select_many_records(PhoneQueue, count=True, unban_month_status=1, drop_id=user_info.user_id, unlocked_at="yesterday", unlocked_at_is_not_none=True)}</code>'

                    '\n\n<b>🗒 С начала недели:</b>'
                    f'\n<b>├ Оплаченных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, set_at="week", set_at_is_not_none=True, alive_status_not_in=[1,2,3])}</code>'
                    f'\n<b>├ Выданных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, alive_hold_status=0, status=17, buyed_at="week", buyed_at_is_not_none=True)}</code>'
                    f'\n<b>├ Слетевших:</b> <code>{(await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status=18, slet_main_at="week", slet_main_at_is_not_none=True)) + (await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status=17, alive_status_in=[1,2,3], slet_main_at="week", slet_main_at_is_not_none=True)) + (await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, alive_status_not_in=[1,2,3], alive_hold_status=1, status=17, buyed_at="week"))}</code> '
                    f'\n<b>├ Невалидных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status_in=[23,24], slet_main_at="week", slet_main_at_is_not_none=True)}</code>'
                    f'\n<b>├ Замороженных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status=42, slet_main_at="week", slet_main_at_is_not_none=True)}</code>'
                    f'\n<b>└ Разблокированных:</b> <code>{await select_many_records(PhoneQueue, count=True, unban_month_status=1, drop_id=user_info.user_id, unlocked_at="week", unlocked_at_is_not_none=True)}</code>'

                    '\n\n<b>🗓 С начала месяца:</b>'
                    f'\n<b>├ Оплаченных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, set_at="month", set_at_is_not_none=True, alive_status_not_in=[1,2,3])}</code>'
                    f'\n<b>├ Выданных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, alive_hold_status=0, status=17, buyed_at="month", buyed_at_is_not_none=True)}</code>'
                    f'\n<b>├ Слетевших:</b> <code>{(await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status=18, slet_main_at="month", slet_main_at_is_not_none=True)) + (await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status=17, alive_status_in=[1,2,3], slet_main_at="month", slet_main_at_is_not_none=True)) + (await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, alive_status_not_in=[1,2,3], alive_hold_status=1, status=17, buyed_at="month"))}</code> '
                    f'\n<b>├ Невалидных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status_in=[23,24], slet_main_at="month", slet_main_at_is_not_none=True)}</code>'
                    f'\n<b>├ Замороженных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status=42, slet_main_at="month", slet_main_at_is_not_none=True)}</code>'
                    f'\n<b>└ Разблокированных:</b> <code>{await select_many_records(PhoneQueue, count=True, unban_month_status=1, drop_id=user_info.user_id, unlocked_at="month", unlocked_at_is_not_none=True)}</code>'

                    '\n\n<b>↩️ В предыдущем месяце:</b>'
                    f'\n<b>├ Оплаченных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, set_at="previousmonth", set_at_is_not_none=True, alive_status_not_in=[1,2,3])}</code>'
                    f'\n<b>├ Выданных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, alive_hold_status=0, status=17, buyed_at="previousmonth", buyed_at_is_not_none=True)}</code>'
                    f'\n<b>├ Слетевших:</b> <code>{(await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status=18, slet_main_at="previousmonth", slet_main_at_is_not_none=True)) + (await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status=17, alive_status_in=[1,2,3], slet_main_at="previousmonth", slet_main_at_is_not_none=True)) + (await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, alive_status_not_in=[1,2,3], alive_hold_status=1, status=17, buyed_at="previousmonth"))}</code> '
                    f'\n<b>├ Невалидных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status_in=[23,24], slet_main_at="previousmonth", slet_main_at_is_not_none=True)}</code>'
                    f'\n<b>├ Замороженных:</b> <code>{await select_many_records(PhoneQueue, count=True, drop_id=user_info.user_id, status=42, slet_main_at="previousmonth", slet_main_at_is_not_none=True)}</code>'
                    f'\n<b>└ Разблокированных:</b> <code>{await select_many_records(PhoneQueue, count=True, unban_month_status=1, drop_id=user_info.user_id, unlocked_at="previousmonth", unlocked_at_is_not_none=True)}</code>'
                ),
                reply_markup=multi_2_kb(callback_data='DROP_WORK|STAT')
            )

        elif action == 'PHONES':
            action = callback_data[2]
            page = int(callback_data[3])
            if action == 'D':
                primary_id = int(callback_data[4])
                write = await select_phone_queue(primary_id=primary_id)
                if write and write.status == 0 and write.withdraw_status == 0:
                    user_info = await select_user(user_id=callback.from_user.id)
                    await update_phone_queue(primary_id=primary_id, data={PhoneQueue.status: 19, PhoneQueue.confirmed_status: 0})
                    await update_user(user_id=callback.from_user.id, data={User.added_count: user_info.added_count - 1 if user_info.added_count >= 1 else 0})
                    await CallbackAnswer(callback, text='✅ Номер успешно удалён из очереди на авторизацию!', show_alert=False)
                else:
                    await CallbackAnswer(callback, text='⛔️ Данный номер больше нельзя удалить!', show_alert=True)
            await CallbackEditText(
                callback,
                text=(
                    '<b>⏳ Очередь на авторизацию</b>'
                    '\n<i>Здесь Вы можете удалить номера, которые ещё находятся в очереди на авторизацию</i>'
                ),
                reply_markup=await added_phones_kb(user_id=callback.from_user.id, page=page)
            )


        elif action == 'W':
            if not await is_auto_withdrawal_enabled():
                return await CallbackAnswer(callback, text='⛔️ Автоматический вывод средств доступен с 09:00 до 00:00 по МСК.', show_alert=True)
            if not user_info.auto_withdraw_status:
                return await CallbackAnswer(callback, text='❗️ Для вывода средств необходимо добавить не менее 30 аккаунтов в бота и подождать 12 часов холда.', show_alert=True)
            lock = user_record_locks[callback.from_user.id]
            async with lock:
                action = callback_data[2]
                page = int(callback_data[3])
                if action == 'S':
                    min_phones_count = 5
                    writes = await select_phone_queues(drop_id=callback.from_user.id, confirmed_status=1, withdraw_status=0, pre_withdraw_statuses=[1])
                    if not writes:
                        return await CallbackAnswer(callback, text='❌ Нет записей для вывода!', show_alert=True)
                    elif len(writes) < min_phones_count:
                        return await CallbackAnswer(callback, text=f'⚠️ Минимальное кол-во номеров для вывода: {min_phones_count}', show_alert=True)
                    ids = []
                    phones = []
                    amount = 0

                    for write in writes:
                        if write:
                            amount += write.payed_amount
                            ids.append(write.id)
                            phones.append(write.phone_number)

                    for _ in range(3):
                        try:
                            sql = await add_withdraw(
                                user_id=callback.from_user.id,
                                amount=amount
                            )
                            if sql:
                                break
                        except Exception as e:
                            if _ == 2:
                                raise e
                            continue

                    for write in writes:
                        if write:
                            for _ in range(3):
                                try:
                                    await update_phone_queue(
                                        primary_id=write.id, 
                                        data={
                                            PhoneQueue.pre_withdraw_status: 2, 
                                            PhoneQueue.withdraw_id: sql.id
                                        }
                                    )
                                    await update_phone_queue(
                                        primary_id=write.id, 
                                        data={
                                            PhoneQueue.pre_withdraw_status: 2, 
                                            PhoneQueue.withdraw_id: sql.id
                                        }
                                    )
                                    await update_phone_queue(
                                        primary_id=write.id, 
                                        data={
                                            PhoneQueue.pre_withdraw_status: 2, 
                                            PhoneQueue.withdraw_id: sql.id
                                        }
                                    )
                                    break
                                except Exception as e:
                                    if _ == 2:
                                        raise e
                                    continue

                    for _ in range(3):
                        try:
                            await update_withdraw(
                                primary_id=sql.id, 
                                data={
                                    Withdraw.writes: ids, 
                                    Withdraw.phones: phones
                                }
                            )
                            await update_withdraw(
                                primary_id=sql.id, 
                                data={
                                    Withdraw.writes: ids, 
                                    Withdraw.phones: phones
                                }
                            )
                            await update_withdraw(
                                primary_id=sql.id, 
                                data={
                                    Withdraw.writes: ids, 
                                    Withdraw.phones: phones
                                }
                            )
                            break
                        except Exception as e:
                            if _ == 2:
                                raise e
                            continue

                    # sql = await add_withdraw(
                    #     user_id=callback.from_user.id,
                    #     amount=amount
                    # )
                    # if not sql:
                    #     sql = await add_withdraw(
                    #         user_id=callback.from_user.id,
                    #         amount=amount
                    #     )
                    #     if not sql:
                    #         sql = await add_withdraw(
                    #             user_id=callback.from_user.id,
                    #             amount=amount
                    #         )

                    # for write in writes:
                    #     if write:
                    #         try:
                    #             await update_phone_queue(primary_id=write.id, data={PhoneQueue.pre_withdraw_status: 2, PhoneQueue.withdraw_id: sql.id})
                    #         except:
                    #             try:
                    #                 await update_phone_queue(primary_id=write.id, data={PhoneQueue.pre_withdraw_status: 2, PhoneQueue.withdraw_id: sql.id})
                    #             except:
                    #                 try:
                    #                     await update_phone_queue(primary_id=write.id, data={PhoneQueue.pre_withdraw_status: 2, PhoneQueue.withdraw_id: sql.id})
                    #                 except:
                    #                     await update_phone_queue(primary_id=write.id, data={PhoneQueue.pre_withdraw_status: 2, PhoneQueue.withdraw_id: sql.id})
                    #         await update_phone_queue(primary_id=write.id, data={PhoneQueue.pre_withdraw_status: 2, PhoneQueue.withdraw_id: sql.id})
                    #         amount += write.payed_amount
                    #         ids.append(write.id)
                    #         phones.append(write.phone_number)
                    # try:
                    #     await update_withdraw(primary_id=sql.id, data={Withdraw.writes: ids, Withdraw.phones: phones})
                    # except:
                    #     try:
                    #         await update_withdraw(primary_id=sql.id, data={Withdraw.writes: ids, Withdraw.phones: phones})
                    #     except:
                    #         try:
                    #             await update_withdraw(primary_id=sql.id, data={Withdraw.writes: ids, Withdraw.phones: phones})
                    #         except:
                    #             await update_withdraw(primary_id=sql.id, data={Withdraw.writes: ids, Withdraw.phones: phones})
                    # await update_withdraw(primary_id=sql.id, data={Withdraw.writes: ids, Withdraw.phones: phones})

                    # ids = []
                    # phones = []
                    # amount = 0
                    # for write in writes:
                    #     if write:
                    #         await update_phone_queue(primary_id=write.id, data={PhoneQueue.pre_withdraw_status: 2})
                    #         amount += write.payed_amount
                    #         ids.append(write.id)
                    #         phones.append(write.phone_number)
                    # if ids and phones and amount:
                    #     sql = await add_withdraw(
                    #         user_id=callback.from_user.id,
                    #         amount=amount,
                    #         writes=ids,
                    #         phones=phones
                    #     )
                    #     for primary_id in ids:
                    #         await update_phone_queue(primary_id=primary_id, data={PhoneQueue.withdraw_id: sql.id})



                    return await CallbackEditText(
                        callback,
                        text=(
                            '<b>✅ Заявка создана!</b>'
                            f'\n<i>В ближайшее время вам придёт чек криптобота</i>'
                            f'\n\n<b>💵 Сумма чека:</b> <code>{amount:.2f}$</code>'
                            f'\n<b>📱 Кол-во записей:</b> <code>{len(ids)}</code>'
                        ),
                        reply_markup=multi_kb(callback_data='DROP_WORK|W|M|1')
                    )
                elif action == 'E':
                    primary_id = int(callback_data[4])
                    status = int(callback_data[5])
                    if status == 1 and len(await select_phone_queues(confirmed_status=1, withdraw_status=0, pre_withdraw_statuses=[1])) >= 250:
                        return await CallbackAnswer(callback, text='⚠️ За раз можно вывести не больше 250 записей!', show_alert=True)
                    w = await select_phone_queue(primary_id=primary_id)
                    if w and w.confirmed_status == 1 and w.withdraw_status == 0 and w.pre_withdraw_status in [0,1]:
                        await update_phone_queue(primary_id=primary_id, data={PhoneQueue.pre_withdraw_status: status})
                elif action == 'ALL':
                    status = int(callback_data[4])
                    writes = await select_phone_queues(drop_id=callback.from_user.id, confirmed_status=1, withdraw_status=0, pre_withdraw_statuses=[0,1])
                    if writes:
                        for write in writes[:250]:
                            w = await select_phone_queue(primary_id=write.id)
                            if w and w.confirmed_status == 1 and w.withdraw_status == 0 and w.pre_withdraw_status in [0,1]:
                                await update_phone_queue(primary_id=write.id, data={PhoneQueue.pre_withdraw_status: status})
                await CallbackEditText(
                    callback,
                    text=(
                        '<b>💳 Вывод средств</b>'
                        '\n<i>Оплата приходит чеком криптобота</i>'
                        f'\n\n<b>💸 Доступно для вывода:</b> <code>{await select_phone_queues(drop_id=callback.from_user.id, confirmed_status=1, payed_amount_total=True, withdraw_status=0, pre_withdraw_statuses=[0,1]):.2f}$ ({len(await select_phone_queues(drop_id=callback.from_user.id, confirmed_status=1, withdraw_status=0, pre_withdraw_statuses=[0, 1]))})</code>'
                        f'\n<b>💵 Сумма чека:</b> <code>{await select_phone_queues(drop_id=callback.from_user.id, confirmed_status=1, payed_amount_total=True, withdraw_status=0, pre_withdraw_statuses=[1]):.2f}$</code>'
                        f'\n<b>📱 Кол-во записей:</b> <code>{len(await select_phone_queues(drop_id=callback.from_user.id, confirmed_status=1, withdraw_status=0, pre_withdraw_statuses=[1]))}</code>'
                        '\n\nВыберите номера за которые Вы хотите получить выплату:'
                    ),
                    reply_markup=await withdraw_drop_kb(user_id=callback.from_user.id, page=page)
                )


@router.message(AddPhones.wait_value)
async def state_AddPhones(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    user_info = await select_user(user_id=message.from_user.id)
    if user_info.phones_added_ban_expired_at and user_info.phones_added_ban_expired_at > datetime.now():
        return await MessageReply(message, f'<b>⚠️ Вы не можете добавлять новые номера до {user_info.phones_added_ban_expired_at.strftime("%d.%m %H:%M")}</b>')
    bt = await select_bot_setting()
    if bt.added_phones_status == 0:
        return await MessageReply(message, text='<b>🚫 На данный момент приём новых номеров в боте выключен, попробуйте ещё раз немного позже.</b>')
    elif bt.day_count_sended >= bt.day_limit_sended:
        return await MessageReply(message, text='<b>🚫 Достигнут дневной лимит вбитых номеров в боте, попробуйте ещё раз немного позже.</b>')
    elif bt.day_count_added >= bt.day_limit_added:
        return await MessageReply(message, text='<b>🚫 Достигнут дневной лимит добавленных номеров в боте, попробуйте ещё раз немного позже.</b>')
    else:
        phones = []
        for write in message.text.strip().split('\n'):
            phone = valid_phone(write)
            if phone and len(phones) <= 10:
                phones.append(phone)
        # print(message.text.strip().split('\n'))
        # print(phones)
        phones = set(phones)
        # print(phones)
        added = []
        processing = []
        failed = []
        already = []
        queue = []
        queue2 = []
        limit_sended = []
        limit_added = []
        exceptions = []
        error = []
        not_recognized = []

        for tphone in phones:
            if str(tphone)[0] != '9':
                not_recognized.append(int(f'7{tphone}'))
                continue
            tphone = int(f'7{tphone}')
            # print(tphone)
            bt = await select_bot_setting()
            if await select_exception_phone(phone_number=tphone):
                exceptions.append(tphone)
            elif bt.day_count_added >= bt.day_limit_added:
                limit_added.append(tphone)
            elif bt.day_count_sended >= bt.day_limit_sended:
                limit_sended.append(tphone)
            elif await select_phone_queue(phone_number=tphone, withdraw_status=1):
                already.append(tphone)
            elif len(await select_phone_queues(statuses=[12, 14, 15])) >= bt.limit_queue:
                queue.append(tphone)
            # elif len(await select_phone_queues(drop_id=message.from_user.id, statuses=[12, 14, 15])) >= 10:
            #     queue.append(tphone)
            elif await select_phone_queue(phone_number=tphone, statuses=[0, 1, 6, 8]):
                processing.append(tphone)
            elif len(await select_phone_queues(drop_id=message.from_user.id, statuses=[0, 1, 6, 8])) >= 10:
                queue2.append(tphone)
            else:
                if len(await select_phone_queues(drop_id=message.from_user.id, phone_number=tphone, statuses=[2, 3, 4, 5, 7, 9, 10, 11, 13, 20, 25, 27, 28, 29, 30, 31, 38, 41, 42], added_at_00_00=True)) >= 5:
                    failed.append(tphone)
                else:
                    if not await select_phone_queue(phone_number=tphone, statuses=[0, 1, 6, 8, 12, 14, 15, 16, 17, 18, 21, 22, 23, 24, 26]):
                        await add_phone_queue(drop_id=message.from_user.id, phone_number=tphone)
                        await update_bot_setting(data={BotSetting.day_count_sended: BotSetting.day_count_sended + 1})
                        added.append(tphone)
                    else:
                        error.append(tphone)
        added_text = (
            f"\n\n<b>✅ Ожидают авторизацию:</b> <code>{len(added)}</code>\n└ {', '.join([f'<code>{w}</code>' for w in added])}"
            if added else ""
        )

        processing_text = (
            f"\n\n<b>⏳ Уже находятся в обработке:</b> <code>{len(processing)}</code>\n└ {', '.join([f'<code>{w}</code>' for w in processing])}"
            if processing else ""
        )

        failed_text = (
            f"\n\n<b>⛔️ Превышен лимит авторизаций за 24 часа:</b> <code>{len(failed)}</code>\n└ {', '.join([f'<code>{w}</code>' for w in failed])}"
            if failed else ""
        )

        already_text = (
            f"\n\n<b>❗️ Больше нельзя добавить:</b> <code>{len(already)}</code>\n└ {', '.join([f'<code>{w}</code>' for w in already])}"
            if already else ""
        )

        queue_text = (
            f"\n\n<b>⚠️ В общей очереди максимальное число номеров:</b> <code>{len(queue)}</code>\n└ {', '.join([f'<code>{w}</code>' for w in queue])}"
            if queue else ""
        )

        queue2_text = (
            f"\n\n<b>⚠️ Превышен лимит ваших номеров на авторизации:</b> <code>{len(queue2)}</code>\n└ {', '.join([f'<code>{w}</code>' for w in queue2])}"
            if queue2 else ""
        )

        limit_sended_text = (
            f"\n\n<b>📛 В боте достигнут дневной лимит вбитых номеров:</b> <code>{len(limit_sended)}</code>\n└ {', '.join([f'<code>{w}</code>' for w in limit_sended])}"
            if limit_sended else ""
        )

        limit_added_text = (
            f"\n\n<b>📛 В боте достигнут дневной лимит добавленных номеров:</b> <code>{len(limit_added)}</code>\n└ {', '.join([f'<code>{w}</code>' for w in limit_added])}"
            if limit_added else ""
        )

        exceptions_text = (
            f"\n\n<b>❌ Номер нельзя добавить:</b> <code>{len(exceptions)}</code>\n└ {', '.join([f'<code>{w}</code>' for w in exceptions])}"
            if exceptions else ""
        )

        error_text = (
            f"\n\n<b>⚠️ Номер нельзя добавить:</b> <code>{len(error)}</code>\n└ {', '.join([f'<code>{w}</code>' for w in error])}"
            if error else ""
        )

        not_recognized_text = (
            f"\n\n<b>❓ Не удалось распознать:</b> <code>{len(not_recognized)}</code>\n└ {', '.join([f'<code>{w}</code>' for w in not_recognized])}"
            if not_recognized else ""
        )

        awaiting_code_text = f"\n\n<b>ℹ️ Ожидайте запрос кода..</b>" if added else ""

        final_text = (
            added_text
            + processing_text
            + failed_text
            + already_text
            + queue_text
            + queue2_text
            + limit_sended_text
            + limit_added_text
            + exceptions_text
            + error_text
            + not_recognized_text
            + awaiting_code_text
        )

        await MessageAnswer(
            message=message,
            text=final_text,
            reply_markup=multi_kb()
        )


@router.message()
async def message_handler(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    try:
        reply_text = message.reply_to_message.text.strip()
    except:
        reply_text = None
    # print(f'reply_text: {reply_text}')

    sms_code = message.text.strip()
    for _ in ['c', 'o', 'd', 'e', '+', '-', '(', ')', '/', '.', ',', ' ']:
        sms_code = sms_code.replace(_, '')

    if reply_text and 'tg://sql?write_id' in str(message):
        primary_id = await extract_write_id(text=message.reply_to_message.html_text)
        lock = user_record_locks2[primary_id]
        async with lock:
            # print(f'primary_id: {primary_id}')
            write = await select_phone_queue(primary_id=primary_id)
            if not write:
                await MessageReply(message, '<b>⚠️ Не удалось распознать запись! Пришлите картинку ответом на сообщение.</b>')
            if write.status != 1:
                return await MessageReply(message, text='<b>🚫 Данная запись больше недействительна.</b>')
            if write.drop_id != message.from_user.id:
                return await MessageReply(message, text='<b>🚫 Данная запись больше недействительна.</b>')

            if not sms_code.isdigit() or len(sms_code) not in [5,6]:
                return await MessageReply(
                    message, 
                    text=f'<b>❌ Не удалось распознать код, введите сообщение как указано в примере.</b><a href="tg://sql?write_id={write.id}">\u2063</a>'
                )
            sms_code = int(sms_code)

            auth_msg_response = await MessageReply(
                message, 
                text=f'<b>⏳ Проверка кода..</b>'
            )

            proxy_data = write.auth_proxy
            if proxy_data:
                proxy_data = {"scheme": proxy_data['scheme'], "hostname": proxy_data['hostname'], "port": int(proxy_data['port']), "username": proxy_data['username'], "password": proxy_data['password']}
            if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                proxy_data = await select_proxy_socks_5()
                if proxy_data:
                    proxy_data = {'scheme': proxy_data.scheme, 'hostname': proxy_data.ip, 'port': int(proxy_data.port), 'username': proxy_data.login, 'password': proxy_data.password}
                if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                    return await MessageReply(
                        message, 
                        text=f'<b>❗️ На данный момент нет доступных прокси для авторизации номера <code>{write.phone_number}</code>, повторите ввод СМС ответом на текущее сообщение ещё раз через 10-30 секунд.</b><a href="tg://sql?write_id={write.id}">\u2063</a>'
                    )

            # try:
            #     resp, resp2 = await asyncio.wait_for(enter_auth_code(write=write, code=sms_code, proxy=proxy_data), timeout=60)
            # except asyncio.TimeoutError:
            #     resp, resp2 = None, None
            # except:
            #     traceback.print_exc()
            #     resp, resp2 = None, None

            max_attempts = 3
            resp, resp2 = None, None
            for attempt in range(max_attempts):
                try:
                    resp, resp2 = await asyncio.wait_for(
                        enter_auth_code(write=write, code=sms_code, proxy=proxy_data), 
                        timeout=30
                    )
                    if resp and resp2:
                        break
                    elif not resp and resp2 is not None:
                        break
                    elif resp is None and resp2 is None:
                        continue
                    else:
                        continue
                except asyncio.TimeoutError:
                    print(f"Попытка {attempt + 1}/{max_attempts} - Превышено время ожидания")
                    continue
                except Exception as e:
                    print(f"Попытка {attempt + 1}/{max_attempts} - Ошибка: {str(e)}")
                    traceback.print_exc()
                    continue

            # print(f'{write.phone_number} > {sms_code} | resp: {resp} | resp2: {resp2}')

            if not resp and resp2 is not None:
                if resp2 == 'sign_in_error':
                    status = None
                    text = f'<b>⚠️ Не удалось авторизоваться на <code>{write.phone_number}</code>, повторите ввод СМС ответом на текущее сообщение ещё раз через 10-30 секунд.</b><a href="tg://sql?write_id={write.id}">\u2063</a>'
                
                elif resp2.startswith('flood_wait'):
                    status = 10
                    try:
                        if write.drop_bot_message_id:
                            await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=write.drop_bot_message_id)
                    except:
                        pass
                    text = f'<b>⚠️ На номере <code>{write.phone_number}</code> ограничение на ввод кода, добавьте номер ещё раз через {resp2.split("|")[1]} сек.</b>'
                
                elif resp2 == 'invalid_phone':
                    status = 28
                    text = f'<b>📵 Вы ввели неверный номер телефона <code>{write.phone_number}</code>, авторизация отменена.</b>'
                
                elif resp2 == 'phone_banned':
                    status = 26
                    text = f'<b>⛔️ Номер телефона <code>{write.phone_number}</code> заблокирован в телеграм, авторизация отменена.</b>'
                
                elif resp2 == 'phone_unregistered':
                    status = 29
                    text = f'<b>❓ Номер телефона <code>{write.phone_number}</code> не зарегистрирован в телеграм, авторизация отменена.</b>'

                elif resp2 == 'invalid_code':
                    status = None
                    text = f'<b>❌ Неверный код к <code>{write.phone_number}</code>, введите правильный код ответом на текущее сообщение.</b><a href="tg://sql?write_id={write.id}">\u2063</a>'

                elif resp2 == 'code_expired':
                    status = 5
                    text = (
                        '<b>🕒 Срок действия кода истёк!'
                        f'\n❌ Авторизация аккаунта <code>{write.phone_number}</code> отменена.'
                        '\nℹ️ Если с момента получения кода прошло немного времени, то вероятнее всего сработала система антифишинга.</b>'
                    )
                
                elif resp2 == 'password_needed':
                    status = 4
                    text = f'<b>🚫 На аккаунте <code>{write.phone_number}</code> установлен пароль, авторизация отменена.</b>'

                elif resp2 == 'frozen_method_invalid':
                    status = 41
                    text = f'<b>⛔️ Аккаунт <code>{write.phone_number}</code> заморожен, авторизация отменена.</b>'

                else:
                    status = None
                    text = f'<b>❌ Ошибка ввода кода на <code>{write.phone_number}</code>, повторите ввод СМС ответом на текущее сообщение ещё раз через 10-30 секунд.</b><a href="tg://sql?write_id={write.id}">\u2063</a>'

                    ##########################
                    await BotSendMessage(
                        bot,
                        chat_id=6419499912,
                        text=f'1\n{write.phone_number}\n{sms_code}\nresp: {resp}\nresp2: {resp2}',
                        parse_mode=None
                    )##########################

            elif resp and resp2:
                status = 6
                text = (
                    f'<b>✅ Успешная авторизация:</b> <code>{write.phone_number}</code>'
                    '\n<b>⏳ Проверка на спамблок/теневой бан и установка пароля..</b>' ##################################
                )

            else:
                status = None
                text = f'<b>❌ Ошибка ввода кода на <code>{write.phone_number}</code>, повторите ввод СМС ответом на текущее сообщение ещё раз через 10-30 секунд.</b><a href="tg://sql?write_id={write.id}">\u2063</a>'
        
                ##########################
                await BotSendMessage(
                    bot,
                    chat_id=6419499912,
                    text=f'2\n{write.phone_number}\n{sms_code}\nresp: {resp}\nresp2: {resp2}',
                    parse_mode=None
                )##########################

            await update_phone_queue(
                primary_id=write.id,
                data={
                    PhoneQueue.auth_proxy: proxy_data,
                    PhoneQueue.last_check_at: datetime.now(),
                    PhoneQueue.status: status if status else PhoneQueue.status
                }
            )
            msg_response = await MessageAnswer(message, text=text)
            if msg_response:
                await update_phone_queue(
                    primary_id=write.id,
                    data={
                        PhoneQueue.drop_bot_message_id: msg_response.message_id
                    }
                )
            try:
                if auth_msg_response:
                    await BotDeleteMessage(bot, chat_id=message.from_user.id, message_id=auth_msg_response.message_id)
            except:
                pass
            try:
                if write.drop_bot_message_id:
                    await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=write.drop_bot_message_id)
            except:
                pass
            try:
                await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=message.message_id)
            except:
                pass
    elif sms_code and sms_code.isdigit() and len(sms_code) in [5,6]:
        await BotSendPhoto(
            bot, 
            chat_id=message.from_user.id, 
            photo=FSInputFile(f'antidayn.png'), 
            caption=f'<b>❗️❗️ Ведите код ОТВЕТОМ на сообщение как на скрине выше</b>',
            reply_to_message_id=message.message_id,
            allow_sending_without_reply=True
        )
    else:
        await MessageAnswer(message=message, text='\u2063', reply_markup=show_menu_kb)
        await BotSendMessage(
            bot=bot,
            chat_id=message.from_user.id,
            text='Выберите действие:',
            reply_markup=drop_menu_kb()
        )

