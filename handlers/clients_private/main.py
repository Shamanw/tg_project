from aiogram import Bot, Router, F, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from database.commands.main import *
from database.commands.users import *
from database.commands.bot_settings import *

from keyboards.inline.misc_kb import *
from keyboards.inline.clients_menu import *

from utils.misc import *
from utils.additionally_bot import *

from config import *

router = Router()



@router.callback_query(F.data == 'SUPPORT')
async def main_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    bt = await select_bot_setting()
    if not bt.support_username:
        return await CallbackAnswer(callback, '✖️', show_alert=True)
    await CallbackEditText(
        callback, 
        text=(
            f'<b>🆘 Поддержка:</b> @{html.quote(bt.support_username)}'
        ), 
        reply_markup=multi_kb()
    )

@router.callback_query(F.data == 'RULES')
async def main_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    bt = await select_bot_setting()
    if not bt.rules:
        return await CallbackAnswer(callback, '✖️', show_alert=True)
    await CallbackEditText(
        callback, 
        text=(
            f'{str(bt.rules)}'
        ), 
        reply_markup=multi_kb()
    )

@router.callback_query(F.data.startswith('PROFILE'))
async def main_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    callback_data = callback.data.split('|')
    action = callback_data[1]

    if action == 'M':
        user = await select_one_record(User, user_id=callback.from_user.id)
        if not user.user_hash:
            user_hash = await generate_random_code()
            await update_user(user_id=callback.from_user.id, data={User.user_hash: user_hash})
        else:
            user_hash = user.user_hash
        days_count = await days_since(user.registered_at)
        lot_name = 'Не установлен'
        def_unique_id = user.def_unique_id
        if def_unique_id:
            if def_unique_id == 111:
                lot_name = 'Без отлеги'
            elif def_unique_id == 222:
                lot_name = 'Слетевшие'
            else:
                qwrite = await select_one_record(OtlegaGroup, unique_id=def_unique_id)
                if qwrite:
                    lot_name = f'Отлега {qwrite.count_days} {await decline_day(int(qwrite.count_days))}'
        await CallbackEditText(
            callback, 
            text=(
                f'<b>👁‍🗨 ID:</b> <code>{callback.from_user.id}</code>'
                f'\n<b>📆 Регистрация:</b> <code>{user.registered_at.strftime("%d.%m.%Y")} ({days_count} {await decline_day(days_count)})</code>'
                f'\n<b>💵 Баланс:</b> <code>{famount(user.balance)}$</code>'
                f'\n<b>💶 Партнёрский счёт:</b> <code>{famount(user.ref_balance)}$</code>'
                f'\n<b>📌 Лот по умолчанию:</b> <code>{lot_name}</code>'
                # f'история покупок'
                # f'рефрералов'
                # f'куплено товаров'
            ), 
            reply_markup=await profile_menu_kb(user)
        )

    elif action == 'LOT_CLEAR':
        await update_user(user_id=callback.from_user.id, data={User.def_unique_id: None})
        await CallbackAnswer(callback, '✅ Лот по умолчанию отвязан!', show_alert=True)

    elif action == 'LINK':
        action = callback_data[2]
        if action == 'M':
            await CallbackEditText(
                callback, 
                text=(
                    '❓ Для привязки баланса к группе <b>пропишите команду</b> <code>/start</code> внутри самой группы и нажмите на кнопку <b>«Привязать свой баланс»</b>'
                ), 
                reply_markup=await multi_new_2_kb(text='🔗 Мои подключения', callback_data='PROFILE|LINK|E|M|1', text2='‹ Назад', callback_data2='PROFILE|M')
            )
        elif action == 'E':
            action = callback_data[3]
            page = int(callback_data[4])
            if action == 'D':
                group_id = int(callback_data[5])
                await delete_record(LinkGroup, user_id=callback.from_user.id, group_id=group_id)
            await CallbackEditText(
                callback, 
                text='<b>🔗 Мои подключения:</b>',
                reply_markup=await client_groups_connections_kb(user_id=callback.from_user.id, page=page)
            )







@router.callback_query(F.data.startswith('PARTNERS'))
async def main_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    callback_data = callback.data.split('|')
    action = callback_data[1]

    if action == 'M':
        user = await select_one_record(User, user_id=callback.from_user.id)
        if not user.user_hash:
            user_hash = await generate_random_code()
            await update_user(user_id=callback.from_user.id, data={User.user_hash: user_hash})
        else:
            user_hash = user.user_hash
        if user.ref_percent:
            ref_percent = user.ref_percent
        else:
            bt = await select_bot_setting()
            ref_percent = bt.ref_percent
        await CallbackEditText(
            callback, 
            text=(
                f'<b>💰 Вы получаете <code>{famount(ref_percent)}%</code> с каждого купленного товара вашим рефералом</b>'
                f'\n\n<b>💶 Партнёрский счёт:</b> <code>{famount(user.ref_balance)}$</code>'
                f'\n<b>👥 Всего приглашено:</b> <code>{await select_many_records(User, count=True, referrer_id=callback.from_user.id)} чел.</code>'
                f'\n\n<b>🔗 Ссылка для приглашения рефералов:</b>'
                f'\n└ <code>https://t.me/{(await bot.get_me()).username}?start={user_hash}</code>'
            ), 
            reply_markup=await partners_menu_kb()
        )