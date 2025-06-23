from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.users import *
from database.commands.groups import *
from database.commands.phones_queue import *
from database.commands.bot_settings import *


async def settings_menu_kb():
    bt = await select_bot_setting()
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f'{"🔘" if bt.manual_status == 0 else "🟢"} Показ мануала',
                    callback_data=f'STNGS|E|manual_status|{1 if bt.manual_status == 0 else 0}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='♻️ Очистить статус прочтения мануала',
                    callback_data=f'STNGS|CLEAR|MANUAL'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'{"🔘" if bt.added_phones_status == 0 else "🟢"} Приём номеров',
                    callback_data=f'STNGS|E|added_phones_status|{1 if bt.added_phones_status == 0 else 0}'
                ),
                InlineKeyboardButton(
                    text=f'{"🔘" if bt.get_phones_status == 0 else "🟢"} Выдача номеров',
                    callback_data=f'STNGS|E|get_phones_status|{1 if bt.get_phones_status == 0 else 0}'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'{"🔘" if bt.accounts_checker_status == 0 else "🟢"} Авточекер аккаунтов',
                    callback_data=f'STNGS|E|accounts_checker_status|{1 if bt.accounts_checker_status == 0 else 0}'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'{"🔘" if bt.proxy_checker_status == 0 else "🟢"} Авточекер прокси',
                    callback_data=f'STNGS|E|proxy_checker_status|{1 if bt.proxy_checker_status == 0 else 0}'
                ),
                InlineKeyboardButton(
                    text=f'{"🔘" if bt.autoload_proxy_status == 0 else "🟢"} Автозагрузка прокси',
                    callback_data=f'STNGS|E|autoload_proxy_status|{1 if bt.autoload_proxy_status == 0 else 0}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔑 Изменить токен автозагрузки прокси',
                    callback_data=f'STNGS|SET|proxy_api_token'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🟰 Лимит вбива',
                    callback_data=f'STNGS|SET|day_limit_sended'
                ),
                InlineKeyboardButton(
                    text='➕ Лимит добавления',
                    callback_data=f'STNGS|SET|day_limit_added'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='📋 Ссылка на мануал',
                    callback_data=f'STNGS|SET|manual_link'
                ),
                InlineKeyboardButton(
                    text='📵 Лимит в очереди',
                    callback_data=f'STNGS|SET|limit_queue'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='💲 Изменить стандартное значение дропов',
                    callback_data=f'STNGS|SET|main_drop_calc_amount'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='💲 Изменить стандартное значение клиентов',
                    callback_data=f'STNGS|SET|main_group_calc_amount'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🎨 Настройки топика',
                    callback_data=f'STNGS|TOPIC'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🆔 ID группы на ОП',
                    callback_data=f'STNGS|SET|op_group_id'
                ),
                InlineKeyboardButton(
                    text='🔗 Ссылка на ОП',
                    callback_data=f'STNGS|SET|op_group_link'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'{"🔘" if bt.auto_kick_group_status == 0 else "🟢"} Автокик из группы',
                    callback_data=f'STNGS|E|auto_kick_group_status|{1 if bt.auto_kick_group_status == 0 else 0}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='📌 Правила',
                    callback_data=f'STNGS|SET|rules'
                ),
                InlineKeyboardButton(
                    text='🆘 Поддержка',
                    callback_data=f'STNGS|SET|support_username'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🤝 Стандартная ставка по рефке',
                    callback_data=f'STNGS|SET|ref_percent'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'{"🔘" if bt.deposit_status == 0 else "🟢"} Пополнение баланса',
                    callback_data=f'STNGS|E|deposit_status|{1 if bt.deposit_status == 0 else 0}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'{"🔘" if bt.pay_manual == 0 else "🟢"} Пополнение USDT',
                    callback_data=f'STNGS|E|pay_manual|{1 if bt.pay_manual == 0 else 0}'
                ),
                InlineKeyboardButton(
                    text=f'{"🔘" if bt.pay_cryptobot == 0 else "🟢"} Пополнение CryptoBot',
                    callback_data=f'STNGS|E|pay_cryptobot|{1 if bt.pay_cryptobot == 0 else 0}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🕒 Макс. время ожидания',
                    callback_data=f'STNGS|SET|usdt_waiting'
                ),
                InlineKeyboardButton(
                    text='🪙 USDT адрес',
                    callback_data=f'STNGS|SET|usdt_address'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔗🤖 Ссылка для вывода средств',
                    callback_data=f'STNGS|SET|cryptobot_main_invoice_url'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔁💵 Конвертер (мин. сумма баланса)',
                    callback_data=f'STNGS|SET|converter_balance_min'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔁👤 Конвертер (макс. кол-во аккаунтов)',
                    callback_data=f'STNGS|SET|converter_limit_accounts'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔁💰 Конвертер (цена за один аккаунт)',
                    callback_data=f'STNGS|SET|converter_account_price'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔁💷 Конвертер (цена за один аккаунт проверки на валид)',
                    callback_data=f'STNGS|SET|converter_valid_price'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔁🔑 Изменить токен автозагрузки прокси для конвертера',
                    callback_data=f'STNGS|SET|converter_proxy_api_token'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'{"🔘" if bt.pslet_status == 0 else "🟢"} Проверка слёта',
                    callback_data=f'STNGS|E|pslet_status|{1 if bt.pslet_status == 0 else 0}'
                ),
                InlineKeyboardButton(
                    text=f'{"🔘" if bt.pslet_nevalid_status == 0 else "🟢"} Проверка невалида',
                    callback_data=f'STNGS|E|pslet_nevalid_status|{1 if bt.pslet_nevalid_status == 0 else 0}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🚨💢 Процент слёта',
                    callback_data=f'STNGS|SET|percent_slet'
                ),
                InlineKeyboardButton(
                    text='🚨☠️ Процент невалидных',
                    callback_data=f'STNGS|SET|percent_nevalid'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🤖📣 ID группы на ОП',
                    callback_data=f'STNGS|SET|op_client_channel_id'
                ),
                InlineKeyboardButton(
                    text='🤖🔗 Ссылка на ОП',
                    callback_data=f'STNGS|SET|op_client_channel_link'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='START'
                ),
                InlineKeyboardButton(
                    text='🔄',
                    callback_data='STNGS|M'
                ),
                InlineKeyboardButton(
                    text='🤖 💵',
                    callback_data='STNGS|CB'
                ),
            ]
        ]
    )
    return markup


async def setting_themes_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🆔 Изменить ID топика',
                    callback_data=f'STNGS|SET|topic_id'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='➕ Создать Заявки',
                    callback_data=f'STNGS|THEME|topic_applications_theme_id'
                )
            ],
            [
                InlineKeyboardButton(
                    text='➕ Создать Успешные выводы',
                    callback_data=f'STNGS|THEME|topic_withdraws_theme_id'
                )
            ],
            [
                InlineKeyboardButton(
                    text='➕ Создать Уведомления CryptoBot',
                    callback_data=f'STNGS|THEME|topic_failed_withdraws_theme_id'
                )
            ],
            [
                InlineKeyboardButton(
                    text='➕ Создать Отсутствие прокси',
                    callback_data=f'STNGS|THEME|topic_not_found_proxy_theme_id'
                )
            ],
            [
                InlineKeyboardButton(
                    text='➕ Создать Невалидные прокси',
                    callback_data=f'STNGS|THEME|topic_errors_proxy_theme_id'
                )
            ],
            [
                InlineKeyboardButton(
                    text='➕ Создать Автозагрузка прокси',
                    callback_data=f'STNGS|THEME|topic_autoload_proxy'
                )
            ],
            [
                InlineKeyboardButton(
                    text='➕ Создать Ошибки',
                    callback_data=f'STNGS|THEME|topic_errors_theme_id'
                )
            ],
            [
                InlineKeyboardButton(
                    text='➕ Создать Номера',
                    callback_data=f'STNGS|THEME|topic_phones_theme_id'
                )
            ],
            [
                InlineKeyboardButton(
                    text='➕ Создать Замороженные аккаунты',
                    callback_data=f'STNGS|THEME|topic_frozen_theme_id'
                )
            ],
            [
                InlineKeyboardButton(
                    text='➕ Создать Баны',
                    callback_data=f'STNGS|THEME|topic_bans_theme_id'
                )
            ],
            [
                InlineKeyboardButton(
                    text='➕ Создать Пополнения USDT',
                    callback_data=f'STNGS|THEME|topic_payments_theme_id'
                )
            ],
            [
                InlineKeyboardButton(
                    text='➕ Создать Пополнения CryptoBot',
                    callback_data=f'STNGS|THEME|topic_cryptobot_payments_theme_id'
                )
            ],
            # [
            #     InlineKeyboardButton(
            #         text='emj',
            #         callback_data=f'STNGS|THEMES'
            #     )
            # ],
            [
                InlineKeyboardButton(
                    text='🔄',
                    callback_data='STNGS|TOPIC'
                )
            ],
            [
                InlineKeyboardButton(
                    text='‹ Назад',
                    callback_data='STNGS|M'
                )
            ]
        ]
    )
    return markup

