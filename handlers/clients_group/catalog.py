from aiogram import Bot, Router, F, html
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from database.commands.main import *
from database.commands.users import *
from database.commands.bot_settings import *

from keyboards.inline.misc_kb import *
from keyboards.inline.group_kb import *

from utils.misc import *
from utils.additionally_bot import *

from states.main_modules import *

from config import *

router = Router()
group_catalog_buy_record_locks = defaultdict(asyncio.Lock)
group_catalog_buy_record_locks_2 = defaultdict(asyncio.Lock)


@router.message(F.text == 'tg')
@router.message(F.text == 'тг')
@router.message(Command("tg", ignore_case=True))
async def main_command(message: Message, bot: Bot, state: FSMContext):
    await BotDeleteMessage(bot, chat_id=message.chat.id, message_id=message.message_id)
    group_id = message.chat.id
    user = await select_user(user_id=message.from_user.id)
    unique_id = user.def_unique_id
    if user and unique_id and (unique_id in [111,222,333] or (await select_one_record(OtlegaGroup, unique_id=unique_id))):
        qwrite = None
        if unique_id == 111:
            account = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True)
        elif unique_id == 222:
            account = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True)
        elif unique_id == 333:
            account = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True)
        else:
            qwrite = await select_one_record(OtlegaGroup, unique_id=unique_id)
            if not qwrite:
                return await MessageAnswer(message, text='<b>✖️ На данный момент по запрашиваему лоту нет аккаунтов в наличии</b>', reply_markup=await delete_kb())
            account = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True)
        if not account:
            return await MessageAnswer(message, text='<b>✖️ На данный момент по запрашиваему лоту нет аккаунтов в наличии</b>', reply_markup=await delete_kb())
        user_with_balance = None
        user_connections = await select_many_records(LinkGroup, group_id=group_id)
        if user_connections:
            for us in user_connections:
                user = await select_one_record(User, user_id=us.user_id, is_banned=0, balance_equals_or_more=account.buyed_amount)
                if user:
                    user_with_balance = user
                    break
        if not user_with_balance:
            return await MessageAnswer(
                message,
                text=(
                    f'<b>❌ Не удалось найти пользователя с балансом, для покупки аккаунта за <code>{famount(account.buyed_amount)}$</code>. Привяжите аккаунт к группе или пополните баланс через ЛС в боте.</b>'
                ),
                reply_markup=await delete_kb()
            )
        user = await select_user(user_id=user.user_id)
        if user.balance < account.buyed_amount:
            return await MessageAnswer(
                message,
                text=(
                    f'<b>❌ Недостаточно средств</b>'
                    f'\n<b>├ Текущий баланс:</b> <code>{famount(user.balance)}$</code>'
                    f'\n<b>├ Необходимо:</b> <code>{famount(account.buyed_amount)}$</code>'
                    f'\n<b>└ Не хватает:</b> <code>{famount(account.buyed_amount - user.balance)}$</code>'
                    f'\n\n<i>Привяжите аккаунт к группе или пополните баланс через ЛС в боте.</i>'
                ),
                reply_markup=await delete_kb()
            )
        if unique_id == 111:
            account = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True)
        elif unique_id == 222:
            account = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True)
        elif unique_id == 333:
            account = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True)
        else:
            account = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True)
        if not account:
            return await MessageAnswer(message, text='<b>✖️ На данный момент по запрашиваему лоту нет аккаунтов в наличии</b>', reply_markup=await delete_kb())
        await update_phone_queue(
            primary_id=account.id,
            data={
                PhoneQueue.pack_id: int(time.time()),
                PhoneQueue.client_id: user.user_id,
                PhoneQueue.group_id: group_id,
                PhoneQueue.group_user_id: message.from_user.id,
                PhoneQueue.status: 36,
                PhoneQueue.last_auth_code: None,
                PhoneQueue.last_check_at: datetime.now(),
                PhoneQueue.updated_at: datetime.now(),
            }
        )
        await update_user(user_id=user.user_id, data={User.balance: User.balance - account.buyed_amount})
        resp = await MessageAnswer(
            message,
            text=(
                f'<b>⏳ Получение кода:</b> <code>{account.phone_number}</code>'
                f"{f'{chr(10)}<b>🕒 Отлега:</b> <code>{account.otlega_count_days} {await decline_day(account.otlega_count_days)}</code>' if account.otlega_count_days else ''}"
                f'\n\n<b>❗️ Отправьте код на указанный номер, у вас есть 5 минут!</b>'
            ),
            reply_markup=await multi_new_kb(text='❌ Отмена', callback_data=f'CATALOG|SMS|CANC|{account.id}')
        )
        # print(f'resp: {resp}')
        # print(resp.message_id)
        if not resp:
            resp = await MessageAnswer(
                message,
                text=(
                    f'<b>⏳ Получение кода:</b> <code>{account.phone_number}</code>'
                    f"{f'{chr(10)}<b>🕒 Отлега:</b> <code>{account.otlega_count_days} {await decline_day(account.otlega_count_days)}</code>' if account.otlega_count_days else ''}"
                    f'\n\n<b>❗️ Отправьте код на указанный номер, у вас есть 5 минут!</b>'
                ),
                reply_markup=await multi_new_kb(text='❌ Отмена', callback_data=f'CATALOG|SMS|CANC|{account.id}')
            )
            if not resp:
                return await MessageAnswer(message, '<b>✖️ Произошла ошибка, попробуйте запросить СМС ещё раз немного позже!</b>', reply_markup=await delete_kb())
            else:
                await update_phone_queue(
                    primary_id=account.id,
                    data={
                        PhoneQueue.group_bot_message_id: resp.message_id,
                    }
                )
        else:
            await update_phone_queue(
                primary_id=account.id,
                data={
                    PhoneQueue.group_bot_message_id: resp.message_id,
                }
            )
    else:
        await MessageAnswer(
            message, 
            text=(
                f'<b>Выберите категорию:</b>'
            ), 
            reply_markup=await catalog_choose_kb()
        )


@router.message(Command(commands=['shop'], ignore_case=True))
async def main_command(message: Message, bot: Bot, state: FSMContext):
    await MessageAnswer(
        message, 
        text=(
            f'<b>Выберите категорию:</b>'
        ), 
        reply_markup=await catalog_choose_kb()
    )


@router.callback_query(F.data.startswith('CATALOG'))
async def main_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    group_id = callback.message.chat.id
    callback_data = callback.data.split('|')
    action = callback_data[1]

    if action == 'M':
        await CallbackEditText(
            callback, 
            text=(
                f'<b>Выберите категорию:</b>'
            ), 
            reply_markup=await catalog_choose_kb()
        )


    elif action == 'LOT_SET':
        action = callback_data[1]
        unique_id = int(callback_data[2])
        await update_user(user_id=callback.from_user.id, data={User.def_unique_id: unique_id})
        await CallbackAnswer(callback, '✅ Теперь при использовании команды «тг», вы будете получать аккаунты из данного лота.', show_alert=True)

    elif action == 'LOT_CLEAR':
        await update_user(user_id=callback.from_user.id, data={User.def_unique_id: None})
        await CallbackAnswer(callback, '✅ Лот по умолчанию отвязан!', show_alert=True)


    elif action == 'MENU':
        unique_id = int(callback_data[2])
        qwrite = None
        if unique_id == 111:
            title = 'Аккаунты без отлеги'
            accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True)
        elif unique_id == 222:
            title = 'Отработанные аккаунты с отлегой'
            accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True)
        elif unique_id == 333:
            title = 'Отработанные аккаунты'
            accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True)
        else:
            qwrite = await select_one_record(OtlegaGroup, unique_id=unique_id)
            if not qwrite:
                return await CallbackAnswer(callback, '✖️ Нет доступных аккаунтов', show_alert=True)
            title = f'Аккаунты с отлегой {qwrite.count_days} {await decline_day(int(qwrite.count_days))}'
            accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True)
        if not accs_count:
            return await CallbackAnswer(callback, '✖️ Нет доступных аккаунтов', show_alert=True)
        amount_text = ''
        if unique_id == 111:
            min_a = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True, sort_asc='buyed_amount')
            max_a = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True, sort_desc='buyed_amount')
        elif unique_id == 222:
            min_a = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True, sort_asc='buyed_amount')
            max_a = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True, sort_desc='buyed_amount')
        elif unique_id == 333:
            min_a = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True, sort_asc='buyed_amount')
            max_a = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True, sort_desc='buyed_amount')
        else:
            min_a = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True, sort_asc='buyed_amount')
            max_a = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True, sort_desc='buyed_amount')
        if min_a or max_a:
            if min_a.buyed_amount != max_a.buyed_amount:
                amount_text = f'\n<b>Стоимость:</b> <code>{famount(min_a.buyed_amount)}$-{famount(max_a.buyed_amount)}$</code>'
            else:
                amount_text = f'\n<b>Стоимость:</b> <code>{famount(min_a.buyed_amount)}$</code>'
        await CallbackEditText(
            callback,
            text=(
                f'<b>{title}</b>'
                f'\n<b>В наличии:</b> <code>{accs_count} шт.</code>'
                f'{amount_text}'
            ),
            reply_markup=await catalog_menu_kb(unique_id=unique_id, qwrite=qwrite)
        )


    elif action == 'SMS':
        action = callback_data[2]
        unique_id = int(callback_data[3])
        lock = group_catalog_buy_record_locks[group_id]
        async with lock:
            if action == 'GET':
                qwrite = None
                if unique_id == 111:
                    account = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True)
                elif unique_id == 222:
                    account = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True)
                elif unique_id == 333:
                    account = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True)
                else:
                    qwrite = await select_one_record(OtlegaGroup, unique_id=unique_id)
                    if not qwrite:
                        return await CallbackAnswer(callback, '✖️ Нет доступных валидных аккаунтов', show_alert=True)
                    account = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True)
                if not account:
                    return await CallbackAnswer(callback, '✖️ Нет доступных валидных аккаунтов', show_alert=True)
                user_with_balance = None
                user_connections = await select_many_records(LinkGroup, group_id=group_id)
                if user_connections:
                    for us in user_connections:
                        user = await select_one_record(User, user_id=us.user_id, is_banned=0, balance_equals_or_more=account.buyed_amount)
                        if user:
                            user_with_balance = user
                            break
                if not user_with_balance:
                    return await CallbackMessageAnswer(
                        callback,
                        text=(
                            f'<b>❌ Не удалось найти пользователя с балансом, для покупки аккаунта за <code>{famount(account.buyed_amount)}$</code>. Привяжите аккаунт к группе или пополните баланс через ЛС в боте.</b>'
                        ),
                        reply_markup=await delete_kb()
                    )
                user = await select_user(user_id=user.user_id)
                if user.balance < account.buyed_amount:
                    return await CallbackMessageAnswer(
                        callback,
                        text=(
                            f'<b>❌ Недостаточно средств</b>'
                            f'\n<b>├ Текущий баланс:</b> <code>{famount(user.balance)}$</code>'
                            f'\n<b>├ Необходимо:</b> <code>{famount(account.buyed_amount)}$</code>'
                            f'\n<b>└ Не хватает:</b> <code>{famount(account.buyed_amount - user.balance)}$</code>'
                            f'\n\n<i>Привяжите аккаунт к группе или пополните баланс через ЛС в боте.</i>'
                        ),
                        reply_markup=await delete_kb()
                    )
                if unique_id == 111:
                    account = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True)
                elif unique_id == 222:
                    account = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True)
                elif unique_id == 333:
                    account = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True)
                else:
                    account = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True)
                if not account:
                    return await CallbackAnswer(callback, '✖️ Нет доступных валидных аккаунтов', show_alert=True)
                await update_phone_queue(
                    primary_id=account.id,
                    data={
                        PhoneQueue.pack_id: int(time.time()),
                        PhoneQueue.client_id: user.user_id,
                        PhoneQueue.group_id: group_id,
                        PhoneQueue.group_user_id: callback.from_user.id,
                        PhoneQueue.status: 36,
                        PhoneQueue.last_auth_code: None,
                        PhoneQueue.last_check_at: datetime.now(),
                        PhoneQueue.updated_at: datetime.now(),
                    }
                )
                await update_user(user_id=user.user_id, data={User.balance: User.balance - account.buyed_amount})
                resp = await CallbackMessageAnswer(
                    callback,
                    text=(
                        f'<b>⏳ Получение кода:</b> <code>{account.phone_number}</code>'
                        f"{f'{chr(10)}<b>🕒 Отлега:</b> <code>{account.otlega_count_days} {await decline_day(account.otlega_count_days)}</code>' if account.otlega_count_days else ''}"
                        f'\n\n<b>❗️ Отправьте код на указанный номер, у вас есть 5 минут!</b>'
                    ),
                    reply_markup=await multi_new_kb(text='❌ Отмена', callback_data=f'CATALOG|SMS|CANC|{account.id}')
                )
                # print(f'resp: {resp}')
                # print(resp.message_id)
                if not resp:
                    resp = await CallbackMessageAnswer(
                        callback,
                        text=(
                            f'<b>⏳ Получение кода:</b> <code>{account.phone_number}</code>'
                            f"{f'{chr(10)}<b>🕒 Отлега:</b> <code>{account.otlega_count_days} {await decline_day(account.otlega_count_days)}</code>' if account.otlega_count_days else ''}"
                            f'\n\n<b>❗️ Отправьте код на указанный номер, у вас есть 5 минут!</b>'
                        ),
                        reply_markup=await multi_new_kb(text='❌ Отмена', callback_data=f'CATALOG|SMS|CANC|{account.id}')
                    )
                    if not resp:
                        return await CallbackMessageAnswer(callback, '<b>✖️ Произошла ошибка, попробуйте запросить СМС ещё раз немного позже!</b>', reply_markup=await delete_kb())
                    else:
                        await update_phone_queue(
                            primary_id=account.id,
                            data={
                                PhoneQueue.group_bot_message_id: resp.message_id,
                            }
                        )
                else:
                    await update_phone_queue(
                        primary_id=account.id,
                        data={
                            PhoneQueue.group_bot_message_id: resp.message_id,
                        }
                    )
            elif action == 'CANC':
                sql_id = int(callback_data[3])
                account = await select_one_record(PhoneQueue, id=sql_id)
                if not account:
                    return await CallbackAnswer(callback, '✖️ Аккаунт недоступен', show_alert=True)
                if account.status != 36:
                    return await CallbackAnswer(callback, '✖️ Данное действие больше недоступно', show_alert=True)
                if account.client_id != callback.from_user.id and account.group_user_id != callback.from_user.id and callback.from_user.id != ADMIN_ID: ###
                    return await CallbackAnswer(callback, '✖️ Аккаунт не принадлежит вам', show_alert=True)
                if account.last_auth_code is not None: 
                    await CallbackEditText(
                        callback,
                        text=(
                            f'<b>✅ Код получен:</b> <code>{account.phone_number}</code>'
                            f"{f'{chr(10)}<b>🕒 Отлега:</b> <code>{account.otlega_count_days} {await decline_day(account.otlega_count_days)}</code>' if account.otlega_count_days else ''}"
                            f'\n<b>🔑 Пароль:</b> <code>{account.password}</code>'
                            f'\n<b>✉️ Код:</b> <code>{account.last_auth_code}</code>'
                        ),
                        # reply_markup=await multi_new_kb(text='🗄 Получить .session', callback_data=f'PACK|GET|SESSION|{account.pack_id}')
                    )
                    return await CallbackAnswer(callback, '✖️ Данное действие больше недоступно', show_alert=True)
                await update_phone_queue(
                    primary_id=account.id,
                    data={
                        PhoneQueue.client_id: None,
                        PhoneQueue.status: 18 if account.alive_status in [2,3,9] else 1,
                        PhoneQueue.last_check_at: datetime.now(),
                        PhoneQueue.updated_at: datetime.now(),
                    }
                )
                await update_user(user_id=account.client_id, data={User.balance: User.balance + account.buyed_amount})
                await BotDeleteMessage(bot, chat_id=callback.message.chat.id, message_id=callback.message.message_id)


    elif action == 'COUNT':
        action = callback_data[2]
        unique_id = int(callback_data[3])
        lock = group_catalog_buy_record_locks_2[group_id]
        async with lock:
            if action == 'M':
                qwrite = None
                if unique_id == 111:
                    title = 'Аккаунты без отлеги'
                    accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True)
                elif unique_id == 222:
                    title = 'Отработанные аккаунты с отлегой'
                    accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True)
                elif unique_id == 333:
                    title = 'Отработанные аккаунты'
                    accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True)
                else:
                    qwrite = await select_one_record(OtlegaGroup, unique_id=unique_id)
                    if not qwrite:
                        return await CallbackAnswer(callback, '✖️ Нет доступных аккаунтов', show_alert=True)
                    title = f'Аккаунты с отлегой {qwrite.count_days} {await decline_day(int(qwrite.count_days))}'
                    accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True)
                if not accs_count:
                    return await CallbackAnswer(callback, '✖️ Нет доступных аккаунтов', show_alert=True)
                amount_text = ''
                if unique_id == 111:
                    min_a = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True, sort_asc='buyed_amount')
                    max_a = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True, sort_desc='buyed_amount')
                elif unique_id == 222:
                    min_a = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True, sort_asc='buyed_amount')
                    max_a = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True, sort_desc='buyed_amount')
                elif unique_id == 333:
                    min_a = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True, sort_asc='buyed_amount')
                    max_a = await select_one_record(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True, sort_desc='buyed_amount')
                else:
                    min_a = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True, sort_asc='buyed_amount')
                    max_a = await select_one_record(PhoneQueue, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True, sort_desc='buyed_amount')
                if min_a or max_a:
                    if min_a.buyed_amount != max_a.buyed_amount:
                        amount_text = f'\n<b>Стоимость:</b> <code>{famount(min_a.buyed_amount)}$-{famount(max_a.buyed_amount)}$</code>'
                    else:
                        amount_text = f'\n<b>Стоимость:</b> <code>{famount(min_a.buyed_amount)}$</code>'
                main_text = (
                    f'<b>{title}</b>'
                    f'\n<b>В наличии:</b> <code>{accs_count} шт.</code>'
                    f'{amount_text}'
                    f'\n\n<b>Введите кол-во для покупки:</b>'
                )
                callback_data_back = f'CATALOG|MENU|{unique_id}|1'
                await CallbackEditText(callback, text=main_text, reply_markup=await multi_new_kb(callback_data=callback_data_back))
                await state.set_state(CountBuy.wait_value)
                await state.update_data(unique_id=unique_id, response_message_id=callback.message.message_id, main_text=main_text, callback_data_back=callback_data_back)
        
            elif action == 'BUY':
                try:
                    max_count = int(callback_data[4])
                    qwrite = None
                    if unique_id == 111:
                        title = 'Аккаунты без отлеги'
                        accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True)
                    elif unique_id == 222:
                        title = 'Отработанные аккаунты с отлегой'
                        accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True)
                    elif unique_id == 333:
                        title = 'Отработанные аккаунты'
                        accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True)
                    else:
                        qwrite = await select_one_record(OtlegaGroup, unique_id=unique_id)
                        if not qwrite:
                            return await CallbackAnswer(callback, '✖️ К сожалению на данный момент в наличии нет доступных аккаунтов.', show_alert=True)
                        title = f'Аккаунты с отлегой {qwrite.count_days} {await decline_day(int(qwrite.count_days))}'
                        accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True)
                    if not accs_count:
                        return await CallbackAnswer(callback, '✖️ К сожалению на данный момент в наличии нет доступных аккаунтов.', show_alert=True)
                    total_amount = 0
                    if unique_id == 111:
                        accs = await select_many_records(PhoneQueue, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True)
                    elif unique_id == 222:
                        accs = await select_many_records(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True)
                    elif unique_id == 333:
                        accs = await select_many_records(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True)
                    else:
                        accs = await select_many_records(PhoneQueue, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True)
                    accs = accs[:max_count]
                    for acc in accs:
                        total_amount += acc.buyed_amount
                    if total_amount <= 0:
                        return await CallbackAnswer(callback, '✖️ К сожалению на данный момент в наличии нет доступных аккаунтов.', show_alert=True)
                    
                    user_with_balance = None
                    user_connections = await select_many_records(LinkGroup, group_id=group_id)
                    if user_connections:
                        for us in user_connections:
                            user = await select_one_record(User, user_id=us.user_id, is_banned=0, balance_equals_or_more=total_amount)
                            if user:
                                user_with_balance = user
                                break
                    if not user_with_balance:
                        return await CallbackMessageAnswer(
                            callback,
                            text=(
                                f'<b>❌ Не удалось найти пользователя с балансом, для покупки аккаунта за <code>{famount(total_amount)}$</code>. Привяжите аккаунт к группе или пополните баланс через ЛС в боте.</b>'
                            ),
                            reply_markup=await delete_kb()
                        )

                    referrer = None
                    referrer_id = None
                    ref_percent = None
                    if user.referrer_id:
                        referrer_id = user.referrer_id
                        referrer = await select_user(user_id=user.referrer_id)
                        if referrer:
                            if user.ref_percent:
                                ref_percent = user.ref_percent
                            else:
                                bt = await select_bot_setting()
                                ref_percent = bt.ref_percent
                    if user.balance < total_amount:
                        return await CallbackMessageAnswer(
                            callback,
                            text=(
                                f'<b>❌ Недостаточно средств</b>'
                                f'\n<b>├ Ваш баланс:</b> <code>{famount(user.balance)}$</code>'
                                f'\n<b>├ Необходимо:</b> <code>{famount(total_amount)}$</code>'
                                f'\n<b>└ Не хватает:</b> <code>{famount(total_amount - user.balance)}$</code>'
                                f'\n\n<i>Привяжите аккаунт к группе или пополните баланс через ЛС в боте.</i>'
                            ),
                            reply_markup=await delete_kb()
                        )
                    referrer_amount_total = 0
                    referrer_amount_total_count = 0
                    success_sessions = 0
                    total_amount = 0
                    pack_id = int(time.time())
                    all_sessions = []
                    for acc in accs:
                        session_folder = await save_convert_session_tdata(pack_id=pack_id, path_folder='convert_users', tele=Path(f'sessions_base/{acc.session_name}.session'), password=acc.password)
                        print(f'session_folder: {session_folder}')
                        if session_folder:
                            user = await select_user(user_id=user.user_id)
                            account_price = acc.buyed_amount
                            if account_price and user.balance >= account_price:
                                acc = await select_one_record(PhoneQueue, id=acc.id)
                                if acc.status in [12, 35] or (acc.status == 18 and unique_id in [222,333]):
                                    if referrer_id and ref_percent:
                                        referrer_amount = (account_price * ref_percent) / 100
                                        referrer_amount_total += referrer_amount
                                        referrer_amount_total_count += 1
                                    else:
                                        referrer_amount = 0
                                    await update_phone_queue(
                                        primary_id=acc.id,
                                        data={
                                            PhoneQueue.pack_id: pack_id,
                                            PhoneQueue.status: 17,
                                            PhoneQueue.client_id: user.user_id,
                                            PhoneQueue.group_id: group_id,
                                            PhoneQueue.group_user_id: callback.from_user.id,
                                            PhoneQueue.updated_at: datetime.now(),
                                            PhoneQueue.buyed_at: datetime.now(),
                                            PhoneQueue.referrer_id: referrer_id,
                                            PhoneQueue.referrer_amount: referrer_amount,
                                        }
                                    )
                                    await update_user(user_id=user.user_id, data={User.balance: User.balance - account_price})
                                    all_sessions.append(session_folder)
                                    success_sessions += 1
                                    total_amount += account_price
                                else:
                                    try:
                                        os.remove(session_folder)
                                    except:
                                        pass
                    if not all_sessions:
                        return await CallbackEditText(
                            callback,
                            text='<b>✖️ Не удалось обработать ваш запрос, попробуйте ещё раз немного позже.</b>',
                            reply_markup=await multi_new_kb(callback_data=f'CATALOG|MENU|{unique_id}|1')
                        )
                    archive_name = f'convert_users/{pack_id}.zip'
                    await add_record(Archive, user_id=user.user_id, group_id=group_id, group_user_id=callback.from_user.id,archive_path=archive_name, amount=total_amount, count_accounts=success_sessions, pack_id=pack_id, added_at=datetime.now())
                    await create_archive_from_folders(all_sessions, archive_name)
                    if referrer_id and ref_percent and referrer_amount and ref_percent:
                        await update_user(user_id=referrer_id, data={User.ref_balance: User.ref_balance + referrer_amount})
                        await BotSendMessage(
                            bot,
                            chat_id=referrer_id,
                            text=f'<b>💸 Вы получили <code>+{famount(referrer_amount)}$</code> (<code>{ref_percent}%</code>) за покупку аккаунта рефералом</b>'
                        )
                    await BotSendDocument(
                        bot,
                        chat_id=callback.message.chat.id,
                        caption=(
                            '<b>📦 Аккаунты готовы к использованию</b>'
                            f'\n<b>├ Кол-во:</b> <code>{success_sessions} шт.</code>'
                            f"{f'{chr(10)}<b>├ Отлега:</b> <code>{qwrite.count_days} {await decline_day(qwrite.count_days)}</code>' if qwrite and qwrite.count_days else ''}"
                            f'\n<b>└ Стоимость:</b> <code>{famount(total_amount)}$</code>'
                        ),
                        document=FSInputFile(archive_name),
                        reply_markup=await multi_new_kb(text='🗄 Получить .session', callback_data=f'PACK|GET|SESSION|{pack_id}')
                    )
                    if all_sessions:
                        for sss in all_sessions:
                            try:
                                os.remove(sss)
                            except:
                                pass
                    try:
                        await BotDeleteMessage(bot, chat_id=callback.message.chat.id, message_id=callback.message.message_id)
                    except:
                        pass
                except Exception as e:
                    traceback.print_exc()
                    print(f'EROEOREOROEROEROEROEOR: {e}', 'CATAL1231231312OO3OOOG')

@router.message(CountBuy.wait_value)
async def handler_state(message: Message, bot: Bot, state: FSMContext):
    try:
        state_data = await state.get_data()
        response_message_id = state_data.get('response_message_id')
        main_text = state_data.get('main_text')
        callback_data_back = state_data.get('callback_data_back')
        unique_id = state_data.get('unique_id')
        await state.clear()
        await BotDeleteMessage(bot, chat_id=message.chat.id, message_id=response_message_id)
        value = message.text.strip().replace('шт.', ' ').replace('  ', ' ')
        if value and value.isdigit() and int(value) > 0:
            value = int(value)
            if value > 1000:
                await MessageReply(message, f'<b>⚠️ Нельзя купить больше 1000 аккаунтов за раз.</b>')
            else:
                if unique_id == 111:
                    accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True)
                elif unique_id == 222:
                    accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True)
                elif unique_id == 333:
                    accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True)
                else:
                    qwrite = await select_one_record(OtlegaGroup, unique_id=unique_id)
                    if not qwrite:
                        return await MessageAnswer(message, text='<b>✖️ К сожалению на данный момент в наличии нет доступных аккаунтов.</b>', reply_markup=await multi_new_kb(callback_data=callback_data_back))
                    accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True)
                if not accs_count:
                    return await MessageAnswer(message, text='<b>✖️ К сожалению на данный момент в наличии нет доступных аккаунтов.</b>', reply_markup=await multi_new_kb(callback_data=callback_data_back))
                if accs_count <= 0:
                    return await MessageAnswer(message, text='<b>✖️ К сожалению на данный момент в наличии нет доступных аккаунтов.</b>', reply_markup=await multi_new_kb(callback_data=callback_data_back))
                total_amount = 0
                accs_count = 0
                if unique_id == 111:
                    accs = await select_many_records(PhoneQueue, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True)
                elif unique_id == 222:
                    accs = await select_many_records(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True)
                elif unique_id == 333:
                    accs = await select_many_records(PhoneQueue, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True)
                else:
                    accs = await select_many_records(PhoneQueue, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True)
                accs = accs[:value]
                for acc in accs:
                    accs_count += 1
                    total_amount += acc.buyed_amount
                if total_amount <= 0:
                    return await MessageAnswer(message, text='<b>✖️ К сожалению на данный момент в наличии нет доступных аккаунтов.</b>', reply_markup=await multi_new_kb(callback_data=callback_data_back))
                if accs_count < value:
                    return await MessageReply(
                        message, 
                        text=(
                            f'<b>❗️ В наличии имеется меньше аккаунтов чем вы запросили: <code>{accs_count}</code> из <code>{value}</code></b>'
                            f'\n<b>💲 Стоимость:</b> <code>{famount(total_amount)}$</code>'
                        ),
                        reply_markup=await multi_new_2_kb(text='✅ Приобрести сколько имеется', callback_data=f'CATALOG|COUNT|BUY|{unique_id}|{accs_count}', text2='❌ Отмена', callback_data2=callback_data_back)
                    )
                else:
                    return await MessageReply(
                        message, 
                        text=(
                            f'<b>👤 Кол-во аккаунтов: <code>{accs_count} шт.</code></b>'
                            f'\n<b>💲 Стоимость:</b> <code>{famount(total_amount)}$</code>'
                        ),
                        reply_markup=await multi_new_2_kb(text='✅ Приобрести', callback_data=f'CATALOG|COUNT|BUY|{unique_id}|{accs_count}', text2='❌ Отмена', callback_data2=callback_data_back)
                    )
        else:
            await MessageReply(message, f'<b>⚠️ Неверное значение. Введите кол-во аккаунтов для покупки в формате цельного числа. (Например: <code>10</code>)</b>')
    except Exception as ex:
        traceback.print_exc()
        await MessageReply(message, f'<b>⚠️ Произошла ошибка при создании заявки на вывод. Попробуйте приобрести товар ещё раз немного позже.</b>')
    response = await MessageAnswer(message, text=main_text, reply_markup=await multi_new_kb(callback_data=callback_data_back))
    await state.set_state(CountBuy.wait_value)
    await state.update_data(unique_id=unique_id, response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back)


@router.callback_query(F.data.startswith('PACK'))
async def main_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    callback_data = callback.data.split('|')
    action = callback_data[1]

    if action == 'GET':
        action = callback_data[2]

        if action == 'SESSION':
            pack_id = int(callback_data[3])
            write = await select_one_record(Archive, pack_id=pack_id)
            if not write:
                return await CallbackAnswer(callback, '✖️ На данный момент архив недоступен', show_alert=True)
            if write.user_id != callback.from_user.id and write.group_user_id != callback.from_user.id and callback.from_user.id != ADMIN_ID: ###
                return await CallbackAnswer(callback, '✖️ Архив не принадлежит вам', show_alert=True)
            if write.take_last_file_at and not await different_time(write.take_last_file_at, 5):
                return await CallbackAnswer(callback, '⚠️ Подождите 5 минут перед следующим запросом', show_alert=True)
            await update_record(Archive, id=write.id, data={Archive.take_last_file_at: datetime.now()})
            files = []
            writes = await select_many_records(PhoneQueue, pack_id=pack_id)
            if not writes:
                return await CallbackAnswer(callback, '✖️ Архив не найден', show_alert=True)
            for write in writes:
                files.append(f'sessions_base/{write.session_name}.session')
            archive_name = f'temp/sessions_{pack_id}.zip'
            await create_archive_from_files(files, archive_name)
            await BotSendDocument(
                bot,
                chat_id=callback.message.chat.id,
                reply_to_message_id=callback.message.message_id,
                allow_sending_without_reply=True,
                document=FSInputFile(archive_name),
                reply_markup=await delete_kb()
            )
            try:
                os.remove(archive_name)
            except:
                pass











