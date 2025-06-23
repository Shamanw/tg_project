from aiogram import Bot, Router, F, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from database.commands.main import *
from database.commands.users import *

from keyboards.inline.misc_kb import *
from keyboards.inline.group_kb import *

from utils.additionally_bot import *
from utils.misc import *

router = Router()


async def main_text(group_id):
    user_connections = await select_many_records(LinkGroup, group_id=group_id)
    total_balance = 0
    if user_connections:
        for us in user_connections:
            user = await select_one_record(User, user_id=us.user_id, is_banned=0, balance_count_less=0)
            # print(user)
            if user:
                total_balance += user.balance
            # else:
            #     await delete_record(LinkGroup, group_id=group_id, user_id=us.user_id)
    return (
        f'\n<b>🆔 ID группы:</b> <code>{group_id}</code>'
        f'\n<b>🔢 Всего привязано балансов:</b> <code>{len(user_connections) if user_connections else "0"}</code>'
        f'\n<b>💸 Баланс группы:</b> <code>{famount(total_balance)}$</code>'
        f'\n<i>Списание происходит с баланса только одного пользователя</i>'
        f'\n<b>🛒 Товары:</b> /shop'
        f'\n<b>📱 Получить номер:</b> /tg или <code>тг</code> или <code>tg</code>'
        f'\n<b>🆘 Поддержка:</b> @{(await select_bot_setting()).support_username}'
    )


@router.message(Command(commands=['start', 'account'], ignore_case=True))
async def start_command(message: Message, bot: Bot, state: FSMContext):
    group_id = message.chat.id
    await MessageAnswer(message, text=await main_text(group_id=group_id), reply_markup=await group_menu_kb(group_id=group_id))

@router.message(Command('support', ignore_case=True))
async def start_command(message: Message, bot: Bot, state: FSMContext):
    await MessageAnswer(message, text=f'<b>🆘 Поддержка:</b> @{(await select_bot_setting()).support_username}', disable_web_page_preview=True)

@router.callback_query(F.data.startswith('gcn'))
async def handler_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await asyncio.sleep(random.uniform(0.1, 0.9))
    group_id = callback.message.chat.id
    callback_data = callback.data.split('|')
    action = callback_data[1]
    group_id = int(callback_data[2])

    if action == 'a':
        if await select_one_record(LinkGroup, group_id=group_id, user_id=callback.from_user.id):
            return await CallbackAnswer(callback, text='🚫 Вы уже привязали свой баланс к данной группе!', show_alert=True)
        await add_record(LinkGroup, group_id=group_id, user_id=callback.from_user.id, added_at=datetime.now(), updated_at=datetime.now())
        await CallbackAnswer(callback, text='🔗 Ваш баланс привязан к данной группе!', show_alert=True)
        user = await select_one_record(User, user_id=callback.from_user.id)
        await BotSendMessage(bot, chat_id=group_id, text=f'<b>🔗 Пользователь <code>{user.user_id}</code> [{f"@{user.username}" if user.username else f"{html.quote(str(user.fullname))}"}] привязал свой баланс к группе!</b>', disable_web_page_preview=True)
        await CallbackEditText(callback, text=await main_text(group_id=group_id), reply_markup=await group_menu_kb(group_id=group_id))

    elif action == 'd':
        if not await select_one_record(LinkGroup, group_id=group_id, user_id=callback.from_user.id):
            return await CallbackAnswer(callback, text='🚫 Вы ещё не привязали свой баланс к данной группе!', show_alert=True)
        await delete_record(LinkGroup, group_id=group_id, user_id=callback.from_user.id)
        await CallbackAnswer(callback, text='❎ Ваш баланс отвязан от данной группы!', show_alert=True)
        user = await select_one_record(User, user_id=callback.from_user.id)
        await BotSendMessage(bot, chat_id=group_id, text=f'<b>❎ Пользователь <code>{user.user_id}</code> [{f"@{user.username}" if user.username else f"{html.quote(str(user.fullname))}"}] отвязал свой баланс от группы!</b>', disable_web_page_preview=True)
        await CallbackEditText(callback, text=await main_text(group_id=group_id), reply_markup=await group_menu_kb(group_id=group_id))

    elif action == 'i':
        us_text = ''
        user_connections = await select_many_records(LinkGroup, group_id=group_id)
        if not user_connections:
            return await CallbackAnswer(callback, text='❌ Никто не привязал баланс!', show_alert=True)
        for us in user_connections:
            user = await select_one_record(User, user_id=us.user_id)
            if user:
                us_text += f'\n<b>👤 <code>{user.user_id}</code> [{f"@{user.username}" if user.username else f"{html.quote(str(user.fullname))}"}]:</b> <code>{famount(user.balance)}$</code>'
            else:
                await delete_record(LinkGroup, group_id=group_id, user_id=us.user_id)
        await BotSendMessage(
            bot,
            chat_id=group_id,
            text=f'<b>Пользователи привязавшие баланс:</b>{us_text}',
            reply_markup=await multi_new_kb(text='❌', callback_data='DELETE'),
            disable_web_page_preview=True
        )

    elif action == 'u':
        await CallbackEditText(callback, text=await main_text(group_id=group_id), reply_markup=await group_menu_kb(group_id=group_id))

