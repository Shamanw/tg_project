from aiogram import Bot, Router, F, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from keyboards.inline.application import admin_application_kb, admin_application_ban_kb
from keyboards.inline.misc_kb import multi_kb

from database.tables import User, Application
from database.commands.users import *
from database.commands.applications import *
from database.commands.bot_settings import *

from utils.misc import *

from utils.additionally_bot import *

from config import ADMIN_ID

router = Router()


@router.callback_query(F.data == 'SUBMIT_APPLICATION')
async def submit_application_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    count_minutes = 30
    user_info = await select_user(user_id=callback.from_user.id)
    user_application = await select_application(user_id=callback.from_user.id)
    if user_info.role != 'client':
        await CallbackAnswer(callback=callback, text=f'❌ Вы не можете подать заявку!', show_alert=True)
    elif user_application and not await different_time(user_application.sended_at, count_minutes):
        await CallbackAnswer(callback=callback, text=f'❌ Вы уже недавно подавали заявку!\n\nПодождите {count_minutes} минут перед подачей новой заявки.', show_alert=True)
    else:
        bt = await select_bot_setting()
        sql = await add_application(user_id=callback.from_user.id)
        fullname = f'{callback.from_user.first_name if callback.from_user.first_name is not None else "отсутствует"}{f" {callback.from_user.last_name}" if callback.from_user.last_name is not None else ""}'
        username = f'''<a href="tg://user?id={callback.from_user.id}">{f'@{callback.from_user.username}' if callback.from_user.username is not None else 'отсутствует'}</a>'''
        text = (
            f'🔔 <a href="https://t.me/{(await bot.get_me()).username}?start=u-{callback.from_user.id}">{html.bold(html.quote(fullname))}</a> <b>запрашивает доступ к функционалу</b>'
            f'\n<b>├ ID:</b> <code>{callback.from_user.id}</code>'
            f'\n<b>├ Логин:</b> {username}'
            f'\n<b>├ Регистрация:</b> {user_info.registered_at.strftime("%d.%m.%Y г. в %H:%M")}'
            f'\n<b>└ Номер заявки в базе:</b> <code>{sql.id}</code>'
        )
        if bt.topic_id and bt.topic_applications_theme_id and bt.topic_applications_theme_id != 0:
            response = await BotSendMessage(
                bot=bot,
                chat_id=bt.topic_id,
                message_thread_id=bt.topic_applications_theme_id,
                text=text,
                reply_markup=admin_application_kb(sql.id),
                disable_web_page_preview=True
            )
            if not response:
                await BotSendMessage(
                    bot=bot,
                    chat_id=ADMIN_ID,
                    text=text,
                    reply_markup=admin_application_kb(sql.id),
                    disable_web_page_preview=True
                )
        else:
            await BotSendMessage(
                bot=bot,
                chat_id=ADMIN_ID,
                text=text,
                reply_markup=admin_application_kb(sql.id),
                disable_web_page_preview=True
            )
        await CallbackAnswer(callback=callback, text='✅ Заявка успешно подана!\n\nОжидайте решения администратора.', show_alert=True)


@router.callback_query(F.data == 'MY_APPLICATIONS')
async def my_applications_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    user_applications = await select_applications(user_id=callback.from_user.id)
    if not user_applications:
        user_applications_text = '<i>у вас нет заявок</i>'
    else:
        user_applications_text = ''
        for user_application in user_applications:
            emoji_status = await get_application_status_emoji(user_application.application_status)
            application_time = user_application.sended_at.strftime("%d.%m.%Y %H:%M")
            text_status = await get_application_status(user_application.application_status)
            user_applications_text += f'{emoji_status} <i>{application_time}</i> — <b>{text_status}</b>\n'
    await CallbackEditText(callback=callback, text=f'<b>✉️ Мои заявки:</b>\n\n{user_applications_text}', reply_markup=multi_kb())


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
        text = str(callback.message.html_text).replace(' <b>запрашивает доступ к функционалу</b>', '').replace('🔔 ', '\n<b>├ ID: </b>')
        await CallbackEditText(callback=callback, text='<b>✅ Заявка одобрена!</b>' + text, reply_markup=await multi_new_2_kb(text='💲 Установить значение', callback_data=f'MNG|U|L|V|1|USD|{application_info.user_id}|1', text2='❌ Закрыть', callback_data2='DELETE'))
        await BotSendMessage(bot=bot, chat_id=application_info.user_id, text=f'<b>✅ Ваша заявка была одобрена!</b>\n\nПропишите /start для обновления меню.')
    elif action == 'NO':
        await update_application(primary_id=application_id, data={Application.application_status: 2})
        text = str(callback.message.html_text).replace(' <b>запрашивает доступ к функционалу</b>', '').replace('🔔 ', '\n<b>├ ID: </b>')
        await CallbackEditText(callback=callback, text='<b>❌ Заявка отклонена!</b>' + text, reply_markup=multi_kb('DELETE', '❌ Закрыть'))
        await BotSendMessage(bot=bot, chat_id=application_info.user_id, text=f'<b>❌ Ваша заявка была отклонена!</b>')
    elif action == 'BAN':
        notification_status = callback_data[3]
        await update_user(user_id=application_info.user_id, data={User.is_banned: 1})
        await update_application(primary_id=application_id, data={Application.application_status: 2})
        text = str(callback.message.html_text).replace(' <b>запрашивает доступ к функционалу</b>', '').replace('🔔 ', '\n<b>├ ID: </b>').replace(' без уведомления', '').replace('<b>✅ Пользователь был разблокирован!</b>', '').replace('<b>🚫 Пользователь был заблокирован!</b>', '')
        await CallbackEditText(callback=callback, text=f'<b>🚫 Пользователь был заблокирован{" без уведомления" if notification_status == "1" else ""}!</b>' + text, reply_markup=admin_application_ban_kb(application_id, '✅ Разбанить', 'UNBAN'))
        if notification_status == '0':
            await BotSendMessage(bot=bot, chat_id=application_info.user_id, text=f'<b>🚫 Вам был ограничен доступ к боту!</b>')
    elif action == 'UNBAN':
        notification_status = callback_data[3]
        await update_user(user_id=application_info.user_id, data={User.is_banned: 0})
        text = str(callback.message.html_text).replace(' <b>запрашивает доступ к функционалу</b>', '').replace('🔔 ', '\n<b>├ ID: </b>').replace(' без уведомления', '').replace('<b>✅ Пользователь был разблокирован!</b>', '').replace('<b>🚫 Пользователь был заблокирован!</b>', '')
        await CallbackEditText(callback=callback, text=f'<b>✅ Пользователь был разблокирован{" без уведомления" if notification_status == "1" else ""}!</b>' + text, reply_markup=admin_application_ban_kb(application_id, '🚫 Забанить', 'BAN'))
        if notification_status == '0':
            await BotSendMessage(bot=bot, chat_id=application_info.user_id, text=f'<b>✅ Вам был восстановлен доступ к боту!</b>')

