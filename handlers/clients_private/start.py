

from aiogram import Bot, Router, F, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from database.commands.main import *

from keyboards.reply.main_kb import show_menu_kb
from keyboards.inline.main_kb import clients_menu_kb

from utils.additionally_bot import *
from utils.misc import *


router = Router()


@router.message(CommandStart(ignore_case=True))
async def command_handler(message: Message, bot: Bot, state: FSMContext, command: CommandObject = None):
    command_args_status = False
    try:
        if command and command.args:
            command_args_status = True
    except:
        command_args_status = False
    user_id = message.from_user.id
    referrer_id = None
    if command_args_status and '-' not in command.args:
        referrer = await select_user(user_hash=command.args)
        if referrer:
            referrer_id = referrer.user_id
    user = await select_user(user_id=user_id)
    if not user:
        await asyncio.sleep(random.uniform(0.000001, 0.0009))
        await add_record(
            User,
            user_id=user_id,
            user_hash=await generate_random_code(),
            referrer_id=referrer_id if referrer_id != user_id else None,
            fullname=f'{message.from_user.first_name} {message.from_user.last_name if message.from_user.last_name else ""}'.strip(),
            username=message.from_user.username,
            registered_at=datetime.now(),
            clients_reg_status=1
        )
    elif user.clients_reg_status == 0:
        await update_record(
            User,
            user_id=user_id,
            data={
                User.referrer_id: referrer_id, 
                User.clients_reg_status: 1,
                User.user_hash: await generate_random_code() if user.user_hash is None else user.user_hash
            }
        )
    await state.clear()
    await MessageAnswer(message, text='Добро пожаловать!', reply_markup=show_menu_kb)
    await MessageAnswer(message, text='Выберите действие:', reply_markup=await clients_menu_kb())


@router.message(F.text == 'ℹ️ Главное меню')
@router.message(Command("menu", "help", "nomer", "stats", "gadd", "gdel", "radd", "rdel", ignore_case=True))
async def message_handler(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    await MessageAnswer(message, text='Выберите действие:', reply_markup=await clients_menu_kb())


@router.callback_query(F.data == 'START')
async def callback_handler(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    await CallbackEditText(callback, text='Выберите действие:', reply_markup=await clients_menu_kb())

