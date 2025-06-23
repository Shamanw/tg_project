import pytz
from decimal import Decimal, ROUND_HALF_UP

from aiogram import Bot, Router, F, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from database.commands.main import *
from database.commands.users import *
from database.commands.payments import *
from database.commands.cryptobot_payments import *
from database.commands.bot_settings import *

from keyboards.inline.main_kb import *
from keyboards.inline.misc_kb import *
from keyboards.inline.deposit_kb import *

from utils.misc import *
from utils.additionally_bot import *

from states.main_modules import *


router = Router()


main_text = (
    '\n\n<b>⏬ Введите сумму в USD, на которую хотите пополнить баланс (минимально от 1$):</b>'
)

main_text_2 = (
    '\n\n<b>⏬ Введите сумму в USD, на которую хотите пополнить баланс (минимально от 1$):</b>'
)

technical_text = '⚠️ В связи с техническими работами на данный момент пополнение недоступно!\n\n❗️ Попробуйте пополнить баланс ещё раз немного позже.'

technical_method_text = '⚠️ Пополнение через данный метод временно недоступно!\n\n❓ Попробуйте ещё раз немного позже или выберите другой метод пополнения.'

@router.message(F.text == 'deposit')
@router.message(Command('deposit', ignore_case=True))
async def handler_command(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    bt = await select_bot_setting()
    if not bt.deposit_status:
        return await MessageAnswer(message, text=f'<b>{technical_text}</b>', reply_markup=await multi_new_2_kb(callback_data='PROFILE|M'))
    await MessageAnswer(
        message,
        text='Выберите способ пополнения:',
        reply_markup=await deposit_choose_kb(callback_data_back='PROFILE|M')
    )

@router.callback_query(F.data == 'deposit')
async def handler_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    bt = await select_bot_setting()
    if not bt.deposit_status:
        return await CallbackAnswer(callback, text=technical_text, show_alert=True)
    await CallbackEditText(
        callback,
        text='Выберите способ пополнения:',
        reply_markup=await deposit_choose_kb(callback_data_back='PROFILE|M')
    )


@router.callback_query(F.data.startswith('pay'))
async def handler_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    callback_data = callback.data.split('|')
    action = callback_data[1]
    bt = await select_bot_setting()
    if not bt.deposit_status:
        return await CallbackAnswer(callback, text=technical_text, show_alert=True)

    if action == 'm':
        action = callback_data[2]

        if action == 'usdt':
            if not bt.pay_manual or not bt.usdt_address:
                return await CallbackAnswer(callback, text=technical_method_text, show_alert=True)
            usdt_address = bt.usdt_address
            response = await CallbackEditText(
                callback,
                text=main_text.format(usdt_address=usdt_address),
                reply_markup=await multi_new_2_kb(callback_data='deposit')
            )
            await state.set_state(DepositBalance.wait_value)
            await state.update_data(
                response_message_id=response.message_id,
                usdt_address=usdt_address
            )
    
        elif action == 'cb':
            if not bt.pay_cryptobot:
                return await CallbackAnswer(callback, text=technical_method_text, show_alert=True)
            response = await CallbackEditText(
                callback,
                text=main_text_2,
                reply_markup=await multi_new_2_kb(callback_data='deposit')
            )
            await state.set_state(DepositBalanceCryptoBot.wait_value)
            await state.update_data(
                response_message_id=response.message_id
            )

        else:
            return await CallbackAnswer(callback, text='⚠️ Выберите другой способ оплаты!', show_alert=True)


@router.message(DepositBalance.wait_value)
async def handler_state(message: Message, bot: Bot, state: FSMContext):
    try:
        state_data = await state.get_data()
        response_message_id = state_data.get('response_message_id')
        usdt_address = state_data.get('usdt_address')
        await state.clear()
        await BotDeleteMessage(bot, chat_id=message.from_user.id, message_id=response_message_id)
        bt = await select_bot_setting()
        if not bt.deposit_status:
            return await MessageAnswer(message, text=f'<b>{technical_text}</b>', reply_markup=await multi_new_2_kb(callback_data='deposit'))
        if not bt.pay_manual:
            return await MessageAnswer(message, text=f'<b>{technical_method_text}</b>', reply_markup=await multi_new_2_kb(callback_data='deposit'))

        amount = message.text.strip().replace(',', '.').replace(' ', '')
        try:
            amount = float(amount)
        except:
            amount = None
        if amount and amount >= 1 and amount <= 99999:
            amount_with_pennies = None
            count_attempts = 0
            while True: 
                if count_attempts <= 99:
                    random_pennies = f'0.0000{random.randint(1, 9)}'
                elif count_attempts <= 999:
                    random_pennies = f'0.000{random.randint(1, 999)}'
                else:
                    random_pennies = f'0.00{random.randint(1, 9999)}'
                amount_with_pennies = float(amount) + float(random_pennies)
                amount_with_pennies = float(f"{amount_with_pennies:.6f}")

                # if count_attempts <= 99:
                #     random_pennies = Decimal('0.00{}'.format(random.randint(1, 99)))
                # elif count_attempts <= 999:
                #     random_pennies = Decimal('0.0{}'.format(str(random.randint(10, 999)).zfill(3)))
                # else:
                #     random_pennies = Decimal('0.{}'.format(str(random.randint(100, 9999)).zfill(4)))
                # amount_with_pennies = Decimal(amount) + random_pennies
                # amount_with_pennies = amount_with_pennies.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
                # print(f'\namount_with_pennies: {amount_with_pennies}')
                if await select_payment(amount_usdt=amount_with_pennies, status=0) is None:
                    break
                count_attempts += 1
            if amount_with_pennies:
                sql = await add_payment(
                    user_id=message.from_user.id,
                    usdt_address=usdt_address,
                    amount_usdt=amount_with_pennies
                )
                response = await MessageAnswer(
                    message,
                    text=(
                        '<b>⏬ Для автоматического пополнения баланса отправьте точную указанную сумму ниже в USDT (TRC20) на адрес:</b>'
                        f'\n\n🪙 <code>{usdt_address}</code>'
                        f'\n<b>└ Точная сумма: <code>{amount_with_pennies}</code> USDT</b>'
                        f'\n\n<b>⏳ Срок ожидания оплаты {bt.usdt_waiting} мин. ОПЛАТИТЕ до {(datetime.now(pytz.timezone("Europe/Moscow")) + timedelta(minutes=bt.usdt_waiting)).strftime("%H:%M")} по МСК.</b>'
                        f'\n\n<b>❗️ Вы должны отправить ТОЧНУЮ сумму с копейками указанную в заявке ботом, если вы отправите иную сумму или сумму без копеек, то платёж не засчитается!</b>'
                    )
                )
                return await update_payment(primary_id=sql.id, data={Payment.message_notify_id: response.message_id})
            else:
                await MessageReply(message, f'<b>⚠️ Неверная сумма!</b>\n\n<b>❗️ Проверьте введённые данные или попробуйте ещё раз немного позже.</b>')
        else:
            await MessageReply(message, f'<b>⚠️ Неверная сумма!</b>\n\n<b>❗️ Проверьте введённые данные или попробуйте ещё раз немного позже.</b>')
    except Exception as ex:
        traceback.print_exc()
        await MessageReply(message, f'<b>⚠️ Произошла ошибка при генерации счёта!</b>\n\n<b>❗️ Проверьте введённые данные или попробуйте ещё раз немного позже.</b>')
    response = await MessageAnswer(
        message,
        text=main_text_2,
        reply_markup=await multi_new_2_kb(callback_data='PROFILE|M')
    )
    await state.set_state(DepositBalance.wait_value)
    await state.update_data(response_message_id=response.message_id, usdt_address=usdt_address)



@router.message(DepositBalanceCryptoBot.wait_value)
async def handler_state(message: Message, bot: Bot, state: FSMContext):
    try:
        state_data = await state.get_data()
        response_message_id = state_data.get('response_message_id')
        await state.clear()
        await BotDeleteMessage(bot, chat_id=message.from_user.id, message_id=response_message_id)
        bt = await select_bot_setting()
        if not bt.deposit_status:
            return await MessageAnswer(message, text=f'<b>{technical_text}</b>', reply_markup=await multi_new_2_kb(callback_data='deposit'))
        if not bt.pay_cryptobot:
            return await MessageAnswer(message, text=f'<b>{technical_method_text}</b>', reply_markup=await multi_new_2_kb(callback_data='deposit'))

        amount = message.text.strip().replace(',', '.').replace(' ', '')
        try:
            amount = float(amount)
        except:
            amount = None
        if amount and amount >= 1 and amount <= 99999:
            invoice_url, error, sql_id = await create_cryptobot_invoice(user_id=message.from_user.id, amount=amount)
            if invoice_url and sql_id:
                response = await MessageAnswer(
                    message,
                    (
                        '<b>⏬ Для автоматического пополнения баланса оплатите данный счёт:</b>'
                        f'\n\n🔗 {invoice_url}'
                        f'\n<b>└ Точная сумма: <code>{amount}</code> USDT</b>'
                        f'\n\n<b>⏳ Срок ожидания оплаты 240 мин. ОПЛАТИТЕ до {(datetime.now(pytz.timezone("Europe/Moscow")) + timedelta(minutes=240)).strftime("%H:%M")} по МСК.</b>'
                    ),
                    disable_web_page_preview=True
                )
                return await update_cryptobot_payment(primary_id=sql_id, data={Payment.message_notify_id: response.message_id})
            else:
                await MessageReply(message, f'<b>⚠️ Произошла ошибка при выставлении счёта!</b>\n\n<b>❗️ Проверьте введённые данные или попробуйте ещё раз немного позже.</b>')
        else:
            await MessageReply(message, f'<b>⚠️ Неверная сумма!</b>\n\n<b>❗️ Проверьте введённые данные или попробуйте ещё раз немного позже.</b>')
    except Exception as ex:
        traceback.print_exc()
        await MessageReply(message, f'<b>⚠️ Произошла ошибка при генерации счёта!</b>\n\n<b>❗️ Проверьте введённые данные или попробуйте ещё раз немного позже.</b>')
    response = await MessageAnswer(
        message,
        text=main_text_2,
        reply_markup=await multi_new_2_kb(callback_data='PROFILE|M')
    )
    await state.set_state(DepositBalanceCryptoBot.wait_value)
    await state.update_data(response_message_id=response.message_id)

