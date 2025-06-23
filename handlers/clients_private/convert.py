from aiogram import Bot, Router, F, html
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from database.commands.main import *
from database.commands.users import *
from database.commands.bot_settings import *
from database.commands.converter_proxy_socks_5 import *

from keyboards.inline.misc_kb import *
from keyboards.inline.convert_menu import *

from utils.misc import *
from utils.tele import *
from utils.additionally_bot import *

from states.main_modules import *

from config import *

router = Router()
convert_queue = defaultdict(asyncio.Lock)



@router.callback_query(F.data.startswith('CONVERT'))
async def main_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    callback_data = callback.data.split('|')
    action = callback_data[1]

    bt = await select_bot_setting()
    converter_balance_min = bt.converter_balance_min
    converter_limit_accounts = bt.converter_limit_accounts
    converter_account_price = bt.converter_account_price
    converter_valid_price = bt.converter_valid_price
    user = await select_user(user_id=callback.from_user.id)

    if user.balance < converter_balance_min:
        return await CallbackAnswer(
            callback,
            text=(
                f'⚠️ Недостаточный баланс для доступа к функционалу!'
                f'\n\nВаш баланс: {famount(user.balance)}$'
                f'\nМинимальный баланс: {famount(converter_balance_min)}$'
            ),
            show_alert=True
        )

    if action == 'M':
        await CallbackEditText(
            callback, 
            text=(
                f'<b>🔁 Конвертер</b>'
                f'\n<b>├ Ваш баланс:</b> <code>{famount(user.balance)}$</code>'
                f'\n<b>├ Цена за один аккаунт:</b> <code>{famount(converter_account_price)}$</code>'
                f'\n<b>├ Цена за один аккаунт проверки на валид:</b> <code>{famount(converter_valid_price)}$</code>'
                f'\n<b>└ Максимальное кол-во аккаунтов за один раз:</b> <code>{converter_limit_accounts} шт.</code> (<code>{famount(converter_limit_accounts * converter_account_price)}$</code>)'
                f'\n\n<b>Выберите действие:</b>'
            ), 
            reply_markup=await convert_menu_kb()
        )

    elif action == 'tdata_to_session_tl':
        await CallbackMessageAnswer(
            callback, 
            text=(
                '<b>🗂 tdata > 🗄 .session (TL)</b>'
                '\n\nДля конвертирования тдаты в сессию telethon, пришлите ответом на текущее сообщение архив с папками которые начинаются на tdata (Например: <code>*/79990001234/tdata/*</code>, <code>*/tdata/*</code>, <code>*/tdata_123/*</code>)'
            ), 
            reply_markup=await delete_kb()
        )

    elif action == 'session_tl_to_tdata':
        await CallbackMessageAnswer(
            callback, 
            text=(
                '<b>🗄 .session (TL) > 🗂 tdata</b>'
                '\n\nДля конвертирования сессии telethon в тдату, пришлите ответом на текущее сообщение архив с файлами которые заканчиваются на .session (Например: <code>79990001234.session</code>)'
            ), 
            reply_markup=await delete_kb()
        )

    elif action == 'valid_session':
        await CallbackMessageAnswer(
            callback, 
            text=(
                '<b>🗄 Проверка на валид: .session (TL)</b>'
                '\n\nДля проверки сессий telethon на валид, пришлите ответом на текущее сообщение архив с файлами которые заканчиваются на .session (Например: <code>79990001234.session</code>)'
            ), 
            reply_markup=await delete_kb()
        )

    elif action == 'valid_tdata':
        await CallbackMessageAnswer(
            callback, 
            text=(
                '<b>🗂 Проверка на валид: tdata</b>'
                '\n\nДля проверки тдаты на валид, пришлите ответом на текущее сообщение архив с папками которые начинаются на tdata (Например: <code>*/79990001234/tdata/*</code>, <code>*/tdata/*</code>, <code>*/tdata_123/*</code>)'
            ), 
            reply_markup=await delete_kb()
        )


async def get_valid_proxy():
    attempts = 30
    while attempts > 0:
        attempts -= 1
        proxy_data = await select_converter_proxy_socks_5()
        if proxy_data:
            proxy_data = {
                'scheme': proxy_data.scheme,
                'hostname': proxy_data.ip,
                'port': int(proxy_data.port),
                'username': proxy_data.login,
                'password': proxy_data.password
            }
            r = await check_proxy(proxy=proxy_data)
            if r:
                return proxy_data
    return None


async def proccessing_document_t1(bot, caption, message, folders, proxy_data, converter_account_price):
    total_sessions = 0
    success_sessions = 0
    failed_sessions = 0
    total_amount = 0
    not_enough_balance = 0
    all_sessions = []
    for index, folder in enumerate(folders):
        print(folder)
        try:
            user = await select_user(user_id=message.from_user.id)
            if user.balance < converter_account_price:
                not_enough_balance += 1
                break
            session_name = f'n{index}_t{int(time.time())}'
            session_path = f"sessions_base/{session_name}.session"
            resp = await convert_tdata_to_telethon_session(tdata=Path(folder), session_path=session_path)
            # resp = await convert_tdata_to_telethon_session(tdata=Path(f'{folder}/tdata'), session_path=session_path)
            if resp:
                total_sessions += 1
                resp1, resp2 = await get_session_for_tdata_adder(session_name=session_name, proxy=proxy_data)
                print(f'resp1: {resp1} | {type(resp2)} resp2: {resp2}')
                if resp1 and resp2 and resp2.phone:
                    phone_number = resp2.phone
                    new_session_path = f"sessions_base/{phone_number}_{int(time.time())}.session"
                    os.rename(session_path, new_session_path)
                    await update_user(user_id=message.from_user.id, data={User.balance: User.balance - converter_account_price})
                    total_amount += converter_account_price
                    success_sessions += 1
                    all_sessions.append(new_session_path)
                else:
                    failed_sessions += 1
            else:
                failed_sessions += 1
        except:
            traceback.print_exc()
    if total_amount:
        await add_record(
            ConvertHistory,
            user_id=message.from_user.id,
            total_amount=total_amount,
            count_writes=success_sessions,
            convert_type=1,
            added_at=datetime.now()
        )

    async def get_stat():
        stats = []
        if len(folders) > 0:
            stats.append(f'<b>Найдено папок:</b> <code>{len(folders)}</code>')
        if total_sessions > 0:
            stats.append(f'<b>Всего сессий:</b> <code>{total_sessions}</code>')
        if failed_sessions > 0:
            stats.append(f'<b>Не удалось конвертировать:</b> <code>{failed_sessions}</code>')
        if total_amount > 0:
            stats.append(f'<b>Списано с баланса:</b> <code>{famount(total_amount)}$</code>')
        if total_amount > 0:
            stats.append(f'<b>Баланс:</b> <code>{famount((await select_user(user_id=message.from_user.id)).balance)}$</code>')
        if not stats:
            return ''
        result = [f'\n├ <b>Конвертировано:</b> <code>{success_sessions}</code>']
        for i, stat in enumerate(stats):
            symbol = '└' if i == len(stats) - 1 else '├'
            result.append(f'{symbol} {stat}')
        return '\n'.join(result)
    not_enought_balance_text = ''
    if not_enough_balance > 0:
        not_enought_balance_text = f'\n\n<i>⚠️ При конвертации у вас закончился баланс, поэтому мы не смогли обработать все файлы.</i>'
    if not all_sessions:
        return await MessageReply(
            message, 
            text=(
                f'<b>❌ Не удалось обработать ни одного файла!</b>'
                f'{await get_stat()}'
                f'{not_enought_balance_text}'
            )
        )
    else:
        try:
            await delete_converter_proxy_socks_5(scheme=proxy_data['scheme'], ip=proxy_data['hostname'], port=proxy_data['port'], login=proxy_data['username'], password=proxy_data['password'])
        except:
            pass
        archive_name = f'convert_users/convert_sessions_{message.from_user.id}_{int(time.time())}.zip'
        await create_archive_from_files(all_sessions, archive_name)
        await BotSendDocument(
            bot,
            chat_id=message.chat.id,
            caption=(
                f'<b>✅ Архив успешно обработан!</b>'
                f'{await get_stat()}'
                f'{not_enought_balance_text}'
            ),
            document=FSInputFile(archive_name)
        )

async def proccessing_document_t2(bot, caption, message, folders, proxy_data, converter_account_price):
    total_tdata = 0
    success_tdata = 0
    failed_tdata = 0
    total_amount = 0
    not_enough_balance = 0
    all_folders = []
    convert_folder = f'convert_users/tdata_files_{int(time.time())}'
    for index, folder in enumerate(folders):
        print(folder)
        try:
            user = await select_user(user_id=message.from_user.id)
            if user.balance < converter_account_price:
                not_enough_balance += 1
                break
            tdata_folder_name = f'{convert_folder}/n{index}_{int(time.time())}'
            resp = await convert_telethon_session_to_tdata(session_path=Path(folder), tdata_folder_name=Path(tdata_folder_name))
            if resp:
                total_tdata += 1
                await update_user(user_id=message.from_user.id, data={User.balance: User.balance - converter_account_price})
                total_amount += converter_account_price
                success_tdata += 1
                all_folders.append(tdata_folder_name)
            else:
                failed_tdata += 1
        except:
            traceback.print_exc()
    if total_amount:
        await add_record(
            ConvertHistory,
            user_id=message.from_user.id,
            total_amount=total_amount,
            count_writes=total_tdata,
            convert_type=2,
            added_at=datetime.now()
        )

    async def get_stat():
        stats = []
        if len(folders) > 0:
            stats.append(f'<b>Найдено сессий:</b> <code>{len(folders)}</code>')
        if total_tdata > 0:
            stats.append(f'<b>Всего тдат:</b> <code>{total_tdata}</code>')
        if failed_tdata > 0:
            stats.append(f'<b>Не удалось конвертировать:</b> <code>{failed_tdata}</code>')
        if total_amount > 0:
            stats.append(f'<b>Списано с баланса:</b> <code>{famount(total_amount)}$</code>')
        if total_amount > 0:
            stats.append(f'<b>Баланс:</b> <code>{famount((await select_user(user_id=message.from_user.id)).balance)}$</code>')
        if not stats:
            return ''
        result = [f'\n├ <b>Конвертировано:</b> <code>{success_tdata}</code>']
        for i, stat in enumerate(stats):
            symbol = '└' if i == len(stats) - 1 else '├'
            result.append(f'{symbol} {stat}')
        return '\n'.join(result)
    not_enought_balance_text = ''
    if not_enough_balance > 0:
        not_enought_balance_text = f'\n\n<i>⚠️ При конвертации у вас закончился баланс, поэтому мы не смогли обработать все файлы.</i>'
    if not all_folders:
        return await MessageReply(
            message, 
            text=(
                f'<b>❌ Не удалось обработать ни одного файла!</b>'
                f'{await get_stat()}'
                f'{not_enought_balance_text}'
            )
        )
    else:
        try:
            await delete_converter_proxy_socks_5(scheme=proxy_data['scheme'], ip=proxy_data['hostname'], port=proxy_data['port'], login=proxy_data['username'], password=proxy_data['password'])
        except:
            pass
        print(f'all_folders: {all_folders}')
        archive_name = f'convert_users/convert_tdata_{message.from_user.id}_{int(time.time())}.zip'
        await create_archive_from_folders2(all_folders, archive_name)
        await BotSendDocument(
            bot,
            chat_id=message.chat.id,
            caption=(
                f'<b>✅ Архив успешно обработан!</b>'
                f'{await get_stat()}'
                f'{not_enought_balance_text}'
            ),
            document=FSInputFile(archive_name)
        )

async def proccessing_document_t3(bot, caption, message, folders, proxy_data, converter_valid_price):
    total_sessions = 0
    success_sessions = 0
    failed_sessions = 0
    error_sessions = 0
    total_amount = 0
    not_enough_balance = 0
    all_sessions = []
    success_folders = []
    for index, folder in enumerate(folders):
        print(folder)
        try:
            user = await select_user(user_id=message.from_user.id)
            if user.balance < converter_valid_price:
                not_enough_balance += 1
                break
            session_name = f'none_n{index}_t{int(time.time())}'
            session_path = f"sessions_base/{session_name}.session"
            resp = await convert_tdata_to_telethon_session(tdata=Path(folder), session_path=session_path)
            # resp = await convert_tdata_to_telethon_session(tdata=Path(f'{folder}/tdata'), session_path=session_path)
            if resp:
                total_sessions += 1
                await update_user(user_id=message.from_user.id, data={User.balance: User.balance - converter_valid_price})
                total_amount += converter_valid_price
                resp1, resp2 = await get_session_for_tdata_adder(session_name=session_name, proxy=proxy_data)
                print(f'resp1: {resp1} | {type(resp2)} resp2: {resp2}')
                if resp1 and resp2 and resp2.phone:
                    phone_number = resp2.phone
                    success_sessions += 1
                    all_sessions.append(session_path)
                    success_folders.append(folder)
                else:
                    failed_sessions += 1
            else:
                error_sessions += 1
        except:
            traceback.print_exc()
    if total_amount:
        await add_record(
            ConvertHistory,
            user_id=message.from_user.id,
            total_amount=total_amount,
            count_writes=total_sessions,
            convert_type=3,
            added_at=datetime.now()
        )

    async def get_stat():
        stats = []
        if len(folders) > 0:
            stats.append(f'<b>Найдено папок:</b> <code>{len(folders)}</code>')
        if total_sessions > 0:
            stats.append(f'<b>Обработано:</b> <code>{total_sessions}</code>')
        if failed_sessions > 0:
            stats.append(f'<b>Невалидных:</b> <code>{failed_sessions}</code>')
        if error_sessions > 0:
            stats.append(f'<b>Не удалось обработать:</b> <code>{error_sessions}</code>')
        if total_amount > 0:
            stats.append(f'<b>Списано с баланса:</b> <code>{famount(total_amount)}$</code>')
        if total_amount > 0:
            stats.append(f'<b>Баланс:</b> <code>{famount((await select_user(user_id=message.from_user.id)).balance)}$</code>')
        if not stats:
            return ''
        result = [f'\n├ <b>Валидных:</b> <code>{success_sessions}</code>']
        for i, stat in enumerate(stats):
            symbol = '└' if i == len(stats) - 1 else '├'
            result.append(f'{symbol} {stat}')
        return '\n'.join(result)
    not_enought_balance_text = ''
    if not_enough_balance > 0:
        not_enought_balance_text = f'\n\n<i>⚠️ При конвертации у вас закончился баланс, поэтому мы не смогли обработать все файлы.</i>'
    if not success_folders:
        return await MessageReply(
            message, 
            text=(
                f'<b>❌ Не удалось обработать ни одного файла!</b>'
                f'{await get_stat()}'
                f'{not_enought_balance_text}'
            )
        )
    else:
        try:
            await delete_converter_proxy_socks_5(scheme=proxy_data['scheme'], ip=proxy_data['hostname'], port=proxy_data['port'], login=proxy_data['username'], password=proxy_data['password'])
        except:
            pass
        archive_name = f'convert_users/valid_tdata_{message.from_user.id}_{int(time.time())}.zip'
        await create_archive_from_folders2(success_folders, archive_name)
        await BotSendDocument(
            bot,
            chat_id=message.chat.id,
            caption=(
                f'<b>✅ Архив успешно обработан!</b>'
                f'{await get_stat()}'
                f'{not_enought_balance_text}'
            ),
            document=FSInputFile(archive_name)
        )

async def proccessing_document_t4(bot, caption, message, folders, proxy_data, converter_valid_price):
    total_tdata = 0
    success_tdata = 0
    failed_tdata = 0
    error_tdata = 0
    total_amount = 0
    not_enough_balance = 0
    all_folders = []
    success_folders = []
    convert_folder = f'convert_users/vtdata_files_{int(time.time())}'
    for index, folder in enumerate(folders):
        print(folder)
        try:
            user = await select_user(user_id=message.from_user.id)
            if user.balance < converter_valid_price:
                not_enough_balance += 1
                break
            tdata_folder_name = f'{convert_folder}/n{index}_{int(time.time())}'
            resp = await convert_telethon_session_to_tdata(session_path=Path(folder), tdata_folder_name=Path(tdata_folder_name))
            total_tdata += 1
            await update_user(user_id=message.from_user.id, data={User.balance: User.balance - converter_valid_price})
            total_amount += converter_valid_price
            if resp:
                success_tdata += 1
                all_folders.append(tdata_folder_name)
                success_folders.append(folder)
            else:
                failed_tdata += 1
        except:
            traceback.print_exc()
    if total_amount:
        await add_record(
            ConvertHistory,
            user_id=message.from_user.id,
            total_amount=total_amount,
            count_writes=total_tdata,
            convert_type=4,
            added_at=datetime.now()
        )

    async def get_stat():
        stats = []
        if len(folders) > 0:
            stats.append(f'<b>Найдено сессий:</b> <code>{len(folders)}</code>')
        if total_tdata > 0:
            stats.append(f'<b>Обработано:</b> <code>{total_tdata}</code>')
        if failed_tdata > 0:
            stats.append(f'<b>Невалидных:</b> <code>{failed_tdata}</code>')
        if error_tdata > 0:
            stats.append(f'<b>Не удалось обработать:</b> <code>{error_tdata}</code>')
        if total_amount > 0:
            stats.append(f'<b>Списано с баланса:</b> <code>{famount(total_amount)}$</code>')
        if total_amount > 0:
            stats.append(f'<b>Баланс:</b> <code>{famount((await select_user(user_id=message.from_user.id)).balance)}$</code>')
        if not stats:
            return ''
        result = [f'\n├ <b>Валидных:</b> <code>{success_tdata}</code>']
        for i, stat in enumerate(stats):
            symbol = '└' if i == len(stats) - 1 else '├'
            result.append(f'{symbol} {stat}')
        return '\n'.join(result)
    not_enought_balance_text = ''
    if not_enough_balance > 0:
        not_enought_balance_text = f'\n\n<i>⚠️ При конвертации у вас закончился баланс, поэтому мы не смогли обработать все файлы.</i>'
    if not success_folders:
        return await MessageReply(
            message, 
            text=(
                f'<b>❌ Не удалось обработать ни одного файла!</b>'
                f'{await get_stat()}'
                f'{not_enought_balance_text}'
            )
        )
    else:
        try:
            await delete_converter_proxy_socks_5(scheme=proxy_data['scheme'], ip=proxy_data['hostname'], port=proxy_data['port'], login=proxy_data['username'], password=proxy_data['password'])
        except:
            pass
        print(f'success_folders: {success_folders}')
        archive_name = f'convert_users/valid_sessions_{message.from_user.id}_{int(time.time())}.zip'
        await create_archive_from_files(success_folders, archive_name)
        await BotSendDocument(
            bot,
            chat_id=message.chat.id,
            caption=(
                f'<b>✅ Архив успешно обработан!</b>'
                f'{await get_stat()}'
                f'{not_enought_balance_text}'
            ),
            document=FSInputFile(archive_name)
        )


@router.message(F.document)
async def handle_document(message: Message, bot: Bot, state: FSMContext):
    try:
        r = await MessageReply(message, '<b>⏳ Обработка архива..</b>')
        try:
            reply_text = message.reply_to_message.text.strip()
        except:
            reply_text = None
        if message.document:

            if reply_text and ('Для конвертирования тдаты в сессию telethon, пришлите ответом на текущее сообщение архив с папками' in reply_text):
                bt = await select_bot_setting()
                converter_balance_min = bt.converter_balance_min
                converter_limit_accounts = bt.converter_limit_accounts
                converter_account_price = bt.converter_account_price
                converter_valid_price = bt.converter_valid_price
                user = await select_user(user_id=message.from_user.id)
                if user.balance < converter_balance_min:
                    return await MessageReply(
                        message,
                        text=(
                            f'<b>⚠️ Недостаточный баланс для доступа к функционалу!</b>'
                            f'\n\n<b>Ваш баланс:</b> <code>{famount(user.balance)}$</code>'
                            f'\n<b>Минимальный баланс:</b> <code>{famount(converter_balance_min)}$</code>'
                        ),
                        reply_markup=await delete_kb()
                    )
                proxy_data = await get_valid_proxy()
                if not proxy_data:
                    await MessageReply(message, '<b>⚠️ Тех. проблемы, обратитесь в поддержку</b>', reply_markup=await delete_kb())
                    bot_settings = {"session": bot.session}
                    aio_bot = Bot(token=BOT_TOKEN, **bot_settings)
                    await BotSendMessage(
                        aio_bot,
                        chat_id=bt.topic_id,
                        message_thread_id=bt.topic_not_found_proxy_theme_id,
                        text=f'<b>❗️ Нет прокси конвертера</b>'
                    )
                    return 
                    # return await MessageReply(message, '<b>❌ На данный момент в базе отсутствуют валидные прокси, пришлите файл ещё раз немного позже.</b>', reply_markup=await delete_kb())
                caption = message.caption
                file_id = message.document.file_id
                file_name = message.document.file_name
                file_ext = file_name.split('.')[-1]
                # if file_ext and file_ext in ['zip', 'rar', '7z']:
                if file_ext and file_ext in ['zip']:
                    file = await bot.get_file(file_id)
                    multi_unique_id = f'{int(time.time())}-tdata-{random.randint(100000, 999999)}-{random.randint(100000, 999999)}'
                    archive_path = f'temp/{multi_unique_id}.{file_ext}'
                    output_path = f'temp/{multi_unique_id}'
                    await bot.download_file(file.file_path, f'temp/{multi_unique_id}.{file_ext}')
                    await extract_tdata(archive_path=archive_path, output_path=output_path, limit=converter_limit_accounts)
                    folders = await get_main_folders(output_path)
                    if not folders:
                        return await MessageReply(message, '<b>❌ Не удалось найти папки tdata в архиве!</b>', reply_markup=await delete_kb())
                    print(f'Folders: {len(folders)} | {folders}')
                    total_amount = len(folders) * converter_account_price
                    if user.balance < total_amount:
                        await MessageReply(
                            message,
                            text=(
                                f'<b>❌ Недостаточно средств</b>'
                                f'\n<b>├ Ваш баланс:</b> <code>{famount(user.balance)}$</code>'
                                f'\n<b>├ Необходимо:</b> <code>{famount(total_amount)}$</code>'
                                f'\n<b>└ Не хватает:</b> <code>{famount(total_amount - user.balance)}$</code>'
                            ),
                            reply_markup=await multi_new_2_kb(text='💳 Пополнить баланс', callback_data='deposit', text2='✖️ Закрыть', callback_data2='DELETE')
                        )
                    else:
                        # await proccessing_document_t1(caption, message, folders, proxy_data)
                        await asyncio.gather(asyncio.create_task(proccessing_document_t1(bot, caption, message, folders, proxy_data, converter_account_price)))
                else:
                    # await MessageReply(message, '<b>❌ Отправьте архив в формате .zip, .rar или .7z</b>', reply_markup=await delete_kb())
                    await MessageReply(message, '<b>❌ Отправьте архив в формате .zip</b>', reply_markup=await delete_kb())
            

            elif reply_text and ('Для конвертирования сессии telethon в тдату, пришлите ответом на текущее сообщение архив с файлами' in reply_text):
                bt = await select_bot_setting()
                converter_balance_min = bt.converter_balance_min
                converter_limit_accounts = bt.converter_limit_accounts
                converter_account_price = bt.converter_account_price
                converter_valid_price = bt.converter_valid_price
                user = await select_user(user_id=message.from_user.id)
                if user.balance < converter_balance_min:
                    return await MessageReply(
                        message,
                        text=(
                            f'<b>⚠️ Недостаточный баланс для доступа к функционалу!</b>'
                            f'\n\n<b>Ваш баланс:</b> <code>{famount(user.balance)}$</code>'
                            f'\n<b>Минимальный баланс:</b> <code>{famount(converter_balance_min)}$</code>'
                        ),
                        reply_markup=await delete_kb()
                    )
                proxy_data = await get_valid_proxy()
                if not proxy_data:
                    await MessageReply(message, '<b>⚠️ Тех. проблемы, обратитесь в поддержку</b>', reply_markup=await delete_kb())
                    bot_settings = {"session": bot.session}
                    aio_bot = Bot(token=BOT_TOKEN, **bot_settings)
                    await BotSendMessage(
                        aio_bot,
                        chat_id=bt.topic_id,
                        message_thread_id=bt.topic_not_found_proxy_theme_id,
                        text=f'<b>❗️ Нет прокси конвертера</b>'
                    )
                    return 
                    # return await MessageReply(message, '<b>❌ На данный момент в базе отсутствуют валидные прокси, пришлите файл ещё раз немного позже.</b>', reply_markup=await delete_kb())
                caption = message.caption
                file_id = message.document.file_id
                file_name = message.document.file_name
                file_ext = file_name.split('.')[-1]
                # if file_ext and file_ext in ['zip', 'rar', '7z']:
                if file_ext and file_ext in ['zip']:
                    file = await bot.get_file(file_id)
                    multi_unique_id = f'{int(time.time())}-sessions-{random.randint(100000, 999999)}-{random.randint(100000, 999999)}'
                    archive_path = f'temp/{multi_unique_id}.{file_ext}'
                    output_path = f'temp/{multi_unique_id}'
                    await bot.download_file(file.file_path, f'temp/{multi_unique_id}.{file_ext}')
                    await extract_session_files(archive_path=archive_path, output_path=output_path, limit=converter_limit_accounts)
                    folders = await get_main_sessions(output_path)
                    if not folders:
                        return await MessageReply(message, '<b>❌ Не удалось найти сессии в архиве!</b>', reply_markup=await delete_kb())
                    print(f'Folders2: {len(folders)} | {folders}')
                    total_amount = len(folders) * converter_account_price
                    if user.balance < total_amount:
                        await MessageReply(
                            message,
                            text=(
                                f'<b>❌ Недостаточно средств</b>'
                                f'\n<b>├ Ваш баланс:</b> <code>{famount(user.balance)}$</code>'
                                f'\n<b>├ Необходимо:</b> <code>{famount(total_amount)}$</code>'
                                f'\n<b>└ Не хватает:</b> <code>{famount(total_amount - user.balance)}$</code>'
                            ),
                            reply_markup=await multi_new_2_kb(text='💳 Пополнить баланс', callback_data='deposit', text2='✖️ Закрыть', callback_data2='DELETE')
                        )
                    else:
                        # await proccessing_document(caption, message, folders, proxy_data)
                        await asyncio.gather(asyncio.create_task(proccessing_document_t2(bot, caption, message, folders, proxy_data, converter_account_price)))
                else:
                    await MessageReply(message, '<b>❌ Отправьте архив в формате .zip</b>', reply_markup=await delete_kb())
                    # await MessageReply(message, '<b>❌ Отправьте архив в формате .zip, .rar или .7z</b>', reply_markup=await delete_kb())





            elif reply_text and ('Для проверки тдаты на валид, пришлите' in reply_text):
                bt = await select_bot_setting()
                converter_balance_min = bt.converter_balance_min
                converter_limit_accounts = bt.converter_limit_accounts
                converter_account_price = bt.converter_account_price
                converter_valid_price = bt.converter_valid_price
                user = await select_user(user_id=message.from_user.id)
                if user.balance < converter_balance_min:
                    return await MessageReply(
                        message,
                        text=(
                            f'<b>⚠️ Недостаточный баланс для доступа к функционалу!</b>'
                            f'\n\n<b>Ваш баланс:</b> <code>{famount(user.balance)}$</code>'
                            f'\n<b>Минимальный баланс:</b> <code>{famount(converter_balance_min)}$</code>'
                        ),
                        reply_markup=await delete_kb()
                    )
                proxy_data = await get_valid_proxy()
                if not proxy_data:
                    await MessageReply(message, '<b>⚠️ Тех. проблемы, обратитесь в поддержку</b>', reply_markup=await delete_kb())
                    bot_settings = {"session": bot.session}
                    aio_bot = Bot(token=BOT_TOKEN, **bot_settings)
                    await BotSendMessage(
                        aio_bot,
                        chat_id=bt.topic_id,
                        message_thread_id=bt.topic_not_found_proxy_theme_id,
                        text=f'<b>❗️ Нет прокси конвертера</b>'
                    )
                    return 
                    # return await MessageReply(message, '<b>❌ На данный момент в базе отсутствуют валидные прокси, пришлите файл ещё раз немного позже.</b>', reply_markup=await delete_kb())
                caption = message.caption
                file_id = message.document.file_id
                file_name = message.document.file_name
                file_ext = file_name.split('.')[-1]
                # if file_ext and file_ext in ['zip', 'rar', '7z']:
                if file_ext and file_ext in ['zip']:
                    file = await bot.get_file(file_id)
                    multi_unique_id = f'{int(time.time())}-tvalid-{random.randint(100000, 999999)}-{random.randint(100000, 999999)}'
                    archive_path = f'temp/{multi_unique_id}.{file_ext}'
                    output_path = f'temp/{multi_unique_id}'
                    await bot.download_file(file.file_path, f'temp/{multi_unique_id}.{file_ext}')
                    await extract_tdata(archive_path=archive_path, output_path=output_path, limit=converter_limit_accounts)
                    folders = await get_main_folders(output_path)
                    if not folders:
                        return await MessageReply(message, '<b>❌ Не удалось найти папки tdata в архиве!</b>', reply_markup=await delete_kb())
                    print(f'Folders: {len(folders)} | {folders}')
                    total_amount = len(folders) * converter_valid_price
                    if user.balance < total_amount:
                        await MessageReply(
                            message,
                            text=(
                                f'<b>❌ Недостаточно средств</b>'
                                f'\n<b>├ Ваш баланс:</b> <code>{famount(user.balance)}$</code>'
                                f'\n<b>├ Необходимо:</b> <code>{famount(total_amount)}$</code>'
                                f'\n<b>└ Не хватает:</b> <code>{famount(total_amount - user.balance)}$</code>'
                            ),
                            reply_markup=await multi_new_2_kb(text='💳 Пополнить баланс', callback_data='deposit', text2='✖️ Закрыть', callback_data2='DELETE')
                        )
                    else:
                        # await proccessing_document_t1(caption, message, folders, proxy_data)
                        await asyncio.gather(asyncio.create_task(proccessing_document_t3(bot, caption, message, folders, proxy_data, converter_valid_price)))
                else:
                    # await MessageReply(message, '<b>❌ Отправьте архив в формате .zip, .rar или .7z</b>', reply_markup=await delete_kb())
                    await MessageReply(message, '<b>❌ Отправьте архив в формате .zip</b>', reply_markup=await delete_kb())
            
            




            elif reply_text and ('Для проверки сессий telethon на валид, пришлите' in reply_text):
                bt = await select_bot_setting()
                converter_balance_min = bt.converter_balance_min
                converter_limit_accounts = bt.converter_limit_accounts
                converter_account_price = bt.converter_account_price
                converter_valid_price = bt.converter_valid_price
                user = await select_user(user_id=message.from_user.id)
                if user.balance < converter_balance_min:
                    return await MessageReply(
                        message,
                        text=(
                            f'<b>⚠️ Недостаточный баланс для доступа к функционалу!</b>'
                            f'\n\n<b>Ваш баланс:</b> <code>{famount(user.balance)}$</code>'
                            f'\n<b>Минимальный баланс:</b> <code>{famount(converter_balance_min)}$</code>'
                        ),
                        reply_markup=await delete_kb()
                    )
                proxy_data = await get_valid_proxy()
                if not proxy_data:
                    await MessageReply(message, '<b>⚠️ Тех. проблемы, обратитесь в поддержку</b>', reply_markup=await delete_kb())
                    bot_settings = {"session": bot.session}
                    aio_bot = Bot(token=BOT_TOKEN, **bot_settings)
                    await BotSendMessage(
                        aio_bot,
                        chat_id=bt.topic_id,
                        message_thread_id=bt.topic_not_found_proxy_theme_id,
                        text=f'<b>❗️ Нет прокси конвертера</b>'
                    )
                    return 
                    # return await MessageReply(message, '<b>❌ На данный момент в базе отсутствуют валидные прокси, пришлите файл ещё раз немного позже.</b>', reply_markup=await delete_kb())
                caption = message.caption
                file_id = message.document.file_id
                file_name = message.document.file_name
                file_ext = file_name.split('.')[-1]
                # if file_ext and file_ext in ['zip', 'rar', '7z']:
                if file_ext and file_ext in ['zip']:
                    file = await bot.get_file(file_id)
                    multi_unique_id = f'{int(time.time())}-svalid-{random.randint(100000, 999999)}-{random.randint(100000, 999999)}'
                    archive_path = f'temp/{multi_unique_id}.{file_ext}'
                    output_path = f'temp/{multi_unique_id}'
                    await bot.download_file(file.file_path, f'temp/{multi_unique_id}.{file_ext}')
                    await extract_session_files(archive_path=archive_path, output_path=output_path, limit=converter_limit_accounts)
                    folders = await get_main_sessions(output_path)
                    print(f'Folders: {len(folders)} | {folders}')
                    if not folders:
                        return await MessageReply(message, '<b>❌ Не удалось найти сессии в архиве!</b>', reply_markup=await delete_kb())
                    total_amount = len(folders) * converter_valid_price
                    if user.balance < total_amount:
                        await MessageReply(
                            message,
                            text=(
                                f'<b>❌ Недостаточно средств</b>'
                                f'\n<b>├ Ваш баланс:</b> <code>{famount(user.balance)}$</code>'
                                f'\n<b>├ Необходимо:</b> <code>{famount(total_amount)}$</code>'
                                f'\n<b>└ Не хватает:</b> <code>{famount(total_amount - user.balance)}$</code>'
                            ),
                            reply_markup=await multi_new_2_kb(text='💳 Пополнить баланс', callback_data='deposit', text2='✖️ Закрыть', callback_data2='DELETE')
                        )
                    else:
                        # await proccessing_document_t1(caption, message, folders, proxy_data)
                        await asyncio.gather(asyncio.create_task(proccessing_document_t4(bot, caption, message, folders, proxy_data, converter_valid_price)))
                else:
                    # await MessageReply(message, '<b>❌ Отправьте архив в формате .zip, .rar или .7z</b>', reply_markup=await delete_kb())
                    await MessageReply(message, '<b>❌ Отправьте архив в формате .zip</b>', reply_markup=await delete_kb())
            
            

    except Exception as ex:
        traceback.print_exc()
        await MessageReply(message, f"❌ Произошла ошибка при обработке архива, попробуйте отправить файл ещё раз немного позже.", reply_markup=await delete_kb())
    finally:
        await BotDeleteMessage(bot, chat_id=message.chat.id, message_id=r.message_id)

