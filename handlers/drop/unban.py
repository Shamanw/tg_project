import re
import pytz

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


@router.callback_query(F.data.startswith('UNBAN|'))
async def main_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    callback_data = callback.data.split('|')
    action = callback_data[1]
    found_text = ''

    if action == 'M':
        total_count = 0
        total_amount = 0
        slet_count = await select_many_records(PhoneQueue, count=True, drop_id=callback.from_user.id, unban_month_status=0, status=18, slet_at='month', slet_at_is_not_none=True)
        nevalid_count = await select_many_records(PhoneQueue, count=True, drop_id=callback.from_user.id, unban_month_status=0, status_in=[23,24], slet_at='month', slet_at_is_not_none=True)
        if slet_count:
            total_count += slet_count
        if nevalid_count:
            total_count += nevalid_count
        if total_count:
            slet_amount = await select_phone_queues(drop_id=callback.from_user.id, unban_month_status=0, status=18, payed_amount_total=True, slet_at_month=True)
            nevalid_amount = await select_phone_queues(drop_id=callback.from_user.id, unban_month_status=0, statuses=[23,24], payed_amount_total=True, slet_at_month=True)
            if slet_amount:
                total_amount += slet_amount
            if nevalid_amount:
                total_amount += nevalid_amount
        # print(f'total_count: {total_count}, total_amount: {total_amount}')
        if total_count and total_amount:
            await CallbackEditText(
                callback, 
                text=(
                    f'<b>Сумма вашего убытка за невалидные и слетевшие аккаунты — <code>{famount(total_amount)}$</code></b>'
                    '\n\nХотите приобрести разблокировку?'
                ),
                reply_markup=multi_2_kb(
                    text='✅ Да', callback_data=f'UNBAN|YES',
                    text_back='❌ Нет', callback_data_back='START',
                ),
            )
        else:
            await CallbackEditText(
                callback, 
                text='<b>❌ На данный момент вам недоступна покупка разблокировки!</b>',
                reply_markup=multi_kb()
            )


    elif action == 'YES':
        last_invoice = await select_one_record(CryptoBotPayment, user_id=callback.from_user.id, status=0, invoice_type=1)
        if last_invoice:
            remaining_time = max(240 - int(round((datetime.now() - last_invoice.added_at).total_seconds() / 60)), 0)
            return await CallbackMessageAnswer(
                callback,
                text=(
                    f'<b>❗️ У вас уже есть недавно выставленный счёт ({last_invoice.added_at.strftime("%d.%m %H:%M")})</b>'
                    f'\n\n🔗 https://t.me/CryptoBot?start={last_invoice.transaction_hash}'
                    f'\n<b>└ Точная сумма: <code>{famount(last_invoice.amount_usdt)}</code> USDT</b>'
                    f'\n\n<b>⏳ Осталось до отмены {remaining_time} мин.</b>'
                ),
                reply_markup=multi_kb(text='✖️ Закрыть', callback_data='DELETE'),
                disable_web_page_preview=True
            )
        total_count = 0
        total_amount = 0
        slet_count = await select_many_records(PhoneQueue, count=True, drop_id=callback.from_user.id, unban_month_status=0, status=18, slet_at='month', slet_at_is_not_none=True)
        nevalid_count = await select_many_records(PhoneQueue, count=True, drop_id=callback.from_user.id, unban_month_status=0, status_in=[23,24], slet_at='month', slet_at_is_not_none=True)
        if slet_count:
            total_count += slet_count
        if nevalid_count:
            total_count += nevalid_count
        if total_count:
            slet_amount = await select_phone_queues(drop_id=callback.from_user.id, unban_month_status=0, status=18, payed_amount_total=True, slet_at_month=True)
            nevalid_amount = await select_phone_queues(drop_id=callback.from_user.id, unban_month_status=0, statuses=[23,24], payed_amount_total=True, slet_at_month=True)
            if slet_amount:
                total_amount += slet_amount
            if nevalid_amount:
                total_amount += nevalid_amount
        # print(f'total_count: {total_count}, total_amount: {total_amount}')
        if total_count and total_amount:
            bt = await select_bot_setting()
            if not bt.deposit_status or not bt.pay_cryptobot:
                return await CallbackAnswer(callback, text='⚠️ Технические работы, нажмите на кнопку ещё раз немного позже', show_alert=True)
            amount = float(str(total_amount))
            invoice_url, error, sql_id = await create_cryptobot_invoice(user_id=callback.from_user.id, amount=amount, invoice_type=1)
            if invoice_url and sql_id:
                writes = []
                slet_writes = await select_many_records(PhoneQueue, drop_id=callback.from_user.id, unban_month_status=0, status=18, slet_at='month', slet_at_is_not_none=True)
                nevalid_writes = await select_many_records(PhoneQueue, drop_id=callback.from_user.id, unban_month_status=0, status_in=[23,24], slet_at='month', slet_at_is_not_none=True)
                if slet_writes:
                    for w in slet_writes:
                        writes.append(w.id)
                if nevalid_writes:
                    for w in nevalid_writes:
                        writes.append(w.id)
                if writes:
                    await add_record(UnbanWrite, sql_id=sql_id, user_id=callback.from_user.id, writes=writes)
                    response = await CallbackMessageAnswer(
                        callback,
                        text=(
                            '<b>⏬ Для автоматического пополнения баланса оплатите данный счёт:</b>'
                            f'\n\n🔗 {invoice_url}'
                            f'\n<b>└ Точная сумма: <code>{famount(amount)}</code> USDT</b>'
                            f'\n\n<b>⏳ Срок ожидания оплаты 240 мин. ОПЛАТИТЕ до {(datetime.now(pytz.timezone("Europe/Moscow")) + timedelta(minutes=240)).strftime("%H:%M")} по МСК.</b>'
                        ),
                        reply_markup=multi_kb(text='✖️ Закрыть', callback_data='DELETE'),
                        disable_web_page_preview=True
                    )
                    await update_cryptobot_payment(primary_id=sql_id, data={Payment.message_notify_id: response.message_id})
                else:
                    return await CallbackAnswer(callback, text='⚠️ Технические работы, нажмите на кнопку ещё раз немного позже', show_alert=True)
            else:
                return await CallbackAnswer(callback, text='⚠️ Технические работы, нажмите на кнопку ещё раз немного позже', show_alert=True)
        else:
            await CallbackEditText(
                callback, 
                text='<b>❌ На данный момент вам недоступна покупка разблокировки!</b>',
                reply_markup=multi_kb()
            )
    