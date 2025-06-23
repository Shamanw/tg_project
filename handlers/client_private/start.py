from aiogram import Bot, Router, F, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from keyboards.reply.main_kb import show_menu_kb
from keyboards.inline.main_kb import client_menu_kb
from keyboards.inline.misc_kb import *

from database.commands.users import select_user

from utils.additionally_bot import *

router = Router()


@router.message(F.text == 'ℹ️ Главное меню')
@router.message(CommandStart(ignore_case=True))
async def start_command(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    await MessageAnswer(message=message, text='\u2063', reply_markup=show_menu_kb)
    await BotSendMessage(
        bot=bot,
        chat_id=message.from_user.id,
        text='Выберите действие:',
        reply_markup=client_menu_kb()
    )


@router.callback_query(F.data == 'START')
async def start_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    user_info = await select_user(user_id=callback.from_user.id)
    if user_info and user_info.is_banned:
        await CallbackEditText(
            callback,
            text=(
                '<b>⛔️ Вы заблокированы в боте по одной из следующих причин:</b> большое количество невалидных/слетевших аккаунтов, нарушение правил бота или другие причины.'
            ),
            reply_markup=multi_2_kb(
                text='Посмотреть статистику номеров', callback_data='SLET|M',
                text_back='Купить разбан', callback_data_back='UNBAN|M',
            ),
            disable_web_page_preview=True
        )
    else:
        await CallbackEditText(callback=callback, text='Выберите действие:', reply_markup=client_menu_kb())

