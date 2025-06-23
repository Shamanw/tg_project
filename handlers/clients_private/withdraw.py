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

from states.main_modules import *

from config import *

router = Router()
withdraw_record_locks = defaultdict(asyncio.Lock)
min_amount_withdraw = 10


@router.callback_query(F.data.startswith('WDRW'))
async def main_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    callback_data = callback.data.split('|')
    action = callback_data[1]

    if action == 'M':
        us = await select_user(user_id=callback.from_user.id)
        if us.ref_balance >= min_amount_withdraw:
            main_text = (
                f'<b>💸 Вывод средств с партнёрского счёта</b>'
                f'\n<b>└ Ваш баланс:</b> <code>{famount(us.ref_balance)}$</code>'
                '\n\nВведите сумму на которую вы хотите вывести баланс:'
            )
            callback_data_back = f'PARTNERS|M'
            response = await CallbackEditText(callback, text=main_text, reply_markup=multi_kb(callback_data=callback_data_back))
            await state.set_state(WithdrawClient.wait_value)
            await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back)
        else:
            await CallbackAnswer(callback, f'Минимальная сумма для вывода: {min_amount_withdraw}$\nВаш баланс: {famount(us.ref_balance)}$', show_alert=True)


@router.message(WithdrawClient.wait_value)
async def handler_state(message: Message, bot: Bot, state: FSMContext):
    try:
        lock = withdraw_record_locks[message.from_user.id]
        async with lock:
            state_data = await state.get_data()
            response_message_id = state_data.get('response_message_id')
            main_text = state_data.get('main_text')
            callback_data_back = state_data.get('callback_data_back')
            await state.clear()
            await BotDeleteMessage(bot, chat_id=message.from_user.id, message_id=response_message_id)
            value = message.text.strip().lower().replace(',', '.').replace('|', '.').replace('/', '.').replace('\\', '.').replace('..', '.').replace('$', '').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ')
            if value and await is_num_calc(value) and float(value) >= min_amount_withdraw:
                value = float(value)
                if value < min_amount_withdraw:
                    await MessageReply(message, f'<b>⚠️ Минимальная сумма для вывода: {min_amount_withdraw}$</b>')
                else:
                    us = await select_user(user_id=message.from_user.id)
                    if us.ref_balance >= min_amount_withdraw:
                        await add_record(
                            Withdraw,
                            user_id=message.from_user.id,
                            amount=value,
                            withdraw_status=10,
                            created_at=datetime.now()
                        )
                        await update_record(User, user_id=message.from_user.id, data={User.ref_balance: User.ref_balance - value})
                        await MessageReply(message, f'<b>✅ Заявка на вывод {famount(value)}$ успешно создана!</b>')
                        return 
                    else:
                        await MessageReply(message, f'<b>⚠️ Недостаточно средств для вывода</b>')
            else:
                await MessageReply(message, f'<b>⚠️ Неверное значение</b>')
    except Exception as ex:
        traceback.print_exc()
        await MessageReply(message, f'<b>⚠️ Произошла ошибка при создании заявки на вывод.</b>')
    response = await MessageAnswer(message, text=main_text, reply_markup=multi_kb(callback_data=callback_data_back))
    await state.set_state(WithdrawClient.wait_value)
    await state.update_data(response_message_id=response.message_id, main_text=main_text, callback_data_back=callback_data_back)

