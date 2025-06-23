from sqlalchemy import *

from database.engine import Base


class UnbanWrite(Base):
    __tablename__ = 'unban_writes'
    id = Column(Integer, primary_key=True, index=True)
    sql_id = Column(BigInteger, index=True)
    user_id = Column(BigInteger, index=True)
    writes = Column(JSON)


class ConvertHistory(Base):
    __tablename__ = 'covert_history'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True)
    total_amount = Column(BigInteger, index=True)
    count_writes = Column(BigInteger, index=True)
    convert_type = Column(BigInteger, index=True)
    added_at = Column(DateTime, index=True)


class Archive(Base):
    __tablename__ = 'archives'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True)
    group_id = Column(BigInteger, index=True)
    group_user_id = Column(BigInteger, index=True)
    archive_path = Column(String, index=True)
    amount = Column(BigInteger, index=True)
    count_accounts = Column(BigInteger, index=True)
    pack_id = Column(BigInteger, index=True)
    added_at = Column(DateTime, index=True)
    take_last_file_at = Column(DateTime, index=True)


class LinkGroup(Base):
    __tablename__ = 'links_groups'
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(BigInteger, index=True)
    user_id = Column(BigInteger, index=True)
    added_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)


class Withdraw(Base):
    __tablename__ = 'withdraws'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True)
    amount = Column(BigInteger, index=True)
    writes = Column(JSON, index=True)
    phones = Column(JSON, index=True)
    withdraw_status = Column(Integer, default=0, index=True)
    notify_status = Column(Integer, default=0, index=True)
    check_id = Column(String, index=True)
    created_at = Column(DateTime, index=True)
    withdraw_at = Column(DateTime, index=True)


class ProxySocks5(Base):
    __tablename__ = 'proxies'
    id = Column(Integer, primary_key=True, index=True)
    scheme = Column(String, index=True)
    login = Column(String, index=True)
    password = Column(String, index=True)
    ip = Column(String, index=True)
    port = Column(String, index=True)
    count_errors = Column(Integer, default=0, index=True)


class ConverterProxySocks5(Base):
    __tablename__ = 'converter_proxies'
    id = Column(Integer, primary_key=True, index=True)
    scheme = Column(String, index=True)
    login = Column(String, index=True)
    password = Column(String, index=True)
    ip = Column(String, index=True)
    port = Column(String, index=True)
    count_errors = Column(Integer, default=0, index=True)

    
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True)
    fullname = Column(String)
    username = Column(String)
    role = Column(String, default='client', index=True) # client, drop, admin
    registered_at = Column(DateTime, index=True)
    is_banned = Column(Integer, default=0, index=True)
    added_count = Column(BigInteger, default=0, index=True)
    calc_amount = Column(BigInteger, default=0, index=True)
    manual_read_status = Column(Integer, default=0, index=True)
    referrer_id = Column(BigInteger, index=True)
    user_hash = Column(String, index=True)
    clients_reg_status = Column(Integer, default=0, index=True)
    balance = Column(BigInteger, default=0, index=True)
    ref_balance = Column(BigInteger, default=0, index=True)
    ref_percent = Column(BigInteger, default=0, index=True)
    def_unique_id = Column(BigInteger, index=True)
    phones_added_ban_expired_at = Column(DateTime, index=True)
    auto_ban_status = Column(Integer, default=0, index=True)
    auto_ban_count = Column(Integer, default=0, index=True)
    auto_withdraw_status = Column(Integer, default=0, index=True)
    hold_check_expired_at = Column(DateTime, index=True)


class PhoneQueue(Base):
    __tablename__ = 'phones_queue'
    id = Column(Integer, primary_key=True, index=True)
    drop_id = Column(BigInteger, index=True)
    client_id = Column(BigInteger, index=True)
    group_id = Column(BigInteger, index=True)
    slet_group_id_1 = Column(BigInteger, index=True)
    slet_group_id_2 = Column(BigInteger, index=True)
    phone_number = Column(String, index=True)
    auth_proxy = Column(JSON, index=True)
    session_name = Column(String, index=True)
    password = Column(String, index=True)
    phone_code_hash = Column(String, index=True)
    last_auth_code = Column(String, index=True)
    added_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)
    withdraw_at = Column(DateTime, index=True)
    set_at = Column(DateTime, index=True)
    confirmed_at = Column(DateTime, index=True)
    sent_code_at = Column(DateTime, index=True)
    last_check_at = Column(DateTime, index=True)
    slet_at = Column(DateTime, index=True)
    error_reason = Column(String, index=True)
    not_proxy_notify_status = Column(Integer, default=0, index=True)
    sent_sms_status = Column(Integer, default=0, index=True)
    confirmed_status = Column(Integer, default=0, index=True) # ???
    status = Column(BigInteger, default=0, index=True)
# 0 - в очереди, 1 - авторизация, 2 - не удалось найти прокси, 3 - дроп не прислал верный смс
# 4 - на аккаунте установлен пароль, 5 - истёк срок действия кода, 6 - авторизован, установка пароля
# 7 - не удалось установить пароль, 8 - пароль установлен, ожидание сброса сессий, 9 - сессии не были сброшены
# 10 - на аккаунте флудвейт, 11 - на аккаунте спамблок, 12 - добавлен, 13 - не удалось авторизоваться
# 14 - клиент взял аккаунт на авторизацию, 15 - клиент запросил смс, 16 - не удалось получить смс
# 17 - подтверждён, 18 - слёт, 19 - удалён дропом, 20 - удалён системой, 21 - удалён выплаченный
# 22 - холд 24 часа из-за того что не пришёл смс, 23 - сессия слетела
# 24 - слетела выплаченная сессия, 25 - дроп отменил авторизацию, 26 - номер заблокирован
# 27 - не удалось отправить смс авторизации, 28 - неверный номер телефона
# 29 - номер не зарегистрирован в тг, 30 - не удалось ввести код авторизации
# 31 - не авторизован, 32 - не удалось получить валидный прокси, 33 - ручной забор тдаты
# 34 - обработка тдаты, 35 - обработка аккаунта (клиентский бот), 36 - запрос кода авторизации (клиентский бот)
# 37 - не удалось отправить сообщение для проверки спамблока, 38 - теневой бан, 39 - не удалось проверить теневой бан
# 40 - проверка на слёт, 41 - аккаунт заморожен, 42 - заморожен выплаченный аккаунт
    group_bot_message_id = Column(BigInteger, index=True)
    group_user_message_id = Column(BigInteger, index=True)
    drop_bot_message_id = Column(BigInteger, index=True)
    drop_user_message_id = Column(BigInteger, index=True) # ???
    waiting_confirm_status = Column(Integer, default=0, index=True)
    withdraw_status = Column(Integer, default=0, index=True)
    pre_withdraw_status = Column(Integer, default=0, index=True)
    cryptobot_admin_notify = Column(Integer, default=0, index=True)
    check_id = Column(String, index=True)
    skip_count = Column(Integer, default=0, index=True)
    skip_group_id_1 = Column(BigInteger, index=True)
    skip_group_id_2 = Column(BigInteger, index=True)
    payed_amount = Column(BigInteger, index=True)
    buyed_amount = Column(BigInteger, index=True)
    readded_at = Column(DateTime, index=True)
    withdraw_id = Column(BigInteger, index=True)
    deleted_at = Column(DateTime, index=True)
    buyed_at = Column(DateTime, index=True)
    otlega_unique_id = Column(BigInteger, index=True)
    otlega_count_days = Column(Integer, index=True)
    client_bot = Column(Integer, default=0, index=True)
    take_last_file_at = Column(DateTime, index=True)
    referrer_id = Column(BigInteger, index=True)
    referrer_amount = Column(BigInteger, index=True)
    group_user_id = Column(BigInteger, index=True)
    pack_id = Column(BigInteger, index=True)
    spamblock_status_check = Column(Integer, default=0, index=True)
    unban_month_status = Column(Integer, default=0, index=True)
    pslet_status = Column(Integer, default=0, index=True)
    shadowban_status_check = Column(Integer, default=0, index=True)
    alive_status = Column(Integer, default=0, index=True)
    alive_check_at = Column(DateTime, index=True)
    unlocked_amount = Column(BigInteger, index=True)
    unlocked_at = Column(DateTime, index=True)
    alive_last_check_status = Column(Integer, default=0, index=True)
    alive_hold_status = Column(Integer, default=0, index=True)
    awd_check_status = Column(Integer, default=0, index=True)
    slet_main_at = Column(DateTime, index=True)
    tdata_status = Column(Integer, default=0, index=True)
    slet_last_at = Column(DateTime, index=True)


class OtlegaGroup(Base):
    __tablename__ = 'otlegra_groups'
    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(BigInteger, index=True)
    count_accounts = Column(Integer, index=True)
    count_days = Column(Integer, index=True)
    refill_accounts_status = Column(Integer, default=0, index=True)
    skip_updates_status = Column(Integer, default=0, index=True)
    added_at = Column(DateTime, index=True)

class OtlegaGroupBase(Base):
    __tablename__ = 'otlegra_groups_connections'
    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(BigInteger, index=True)
    group_id = Column(BigInteger, index=True)
    added_at = Column(DateTime, index=True)


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(BigInteger, index=True)
    group_name = Column(String, index=True)
    created_at = Column(DateTime, index=True)
    closed_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)
    work_status = Column(Integer, default=1, index=True)
    group_link = Column(String, index=True)
    cross_timeout = Column(Integer, index=True, default=120)
    calc_amount = Column(BigInteger, default=0, index=True)


class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True)
    application_status = Column(Integer, default=0, index=True) # 0 - на рассмотрении, 1 - одобрена, 2 - отклонена
    sended_at = Column(DateTime, index=True)


class ExceptionPhone(Base):
    __tablename__ = 'exception_phones'
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(BigInteger, index=True)
    added_at = Column(DateTime, index=True)


class SchedulerText(Base):
    __tablename__ = 'scheduler_text'
    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(BigInteger, index=True)
    text = Column(String)
    file_name = Column(String)
    disable_web_page_preview = Column(Boolean)
    added_at = Column(DateTime, index=True)


class SchedulerGroup(Base):
    __tablename__ = 'scheduler_groups'
    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(BigInteger, index=True)
    group_id = Column(BigInteger, index=True)
    period = Column(BigInteger, index=True)
    period_minutes = Column(BigInteger, index=True)
    added_at = Column(DateTime, index=True)
    last_sended_at = Column(DateTime, index=True)
    next_sended_at = Column(DateTime, index=True)


class SavedMassIds(Base):
    __tablename__ = 'saved_mass_ids'
    id = Column(Integer, primary_key=True, index=True)
    ids = Column(String)
    message_id = Column(BigInteger, index=True)
    added_at = Column(DateTime, index=True)


class SchedulerBot(Base):
    __tablename__ = 'scheduler_bot'
    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(BigInteger, index=True)
    period = Column(BigInteger, index=True)
    period_minutes = Column(BigInteger, index=True)
    added_at = Column(DateTime, index=True)
    last_sended_at = Column(DateTime, index=True)
    next_sended_at = Column(DateTime, index=True)
    ids_remove = Column(String)
    enable_status = Column(Integer, default=0, index=True)

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True)
    from_address = Column(String, index=True)
    usdt_address = Column(String, index=True)
    transaction_hash = Column(String, index=True)
    message_notify_id = Column(BigInteger, index=True)
    status = Column(Integer, index=True, default=0) # 0 - на рассмотрении, 1 - оплачен, 2 - отменён, 3 - отменён окончательно, 4 - ошибка
    amount_usdt = Column(BigInteger, index=True)
    timestamp = Column(BigInteger, index=True)
    added_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)
    error_message = Column(String)

class CryptoBotPayment(Base):
    __tablename__ = 'cryptobot_payments'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True)
    invoice_id = Column(BigInteger, index=True)
    transaction_hash = Column(String, index=True)
    message_notify_id = Column(BigInteger, index=True)
    status = Column(Integer, index=True, default=0) # 0 - ожидает оплаты, 1 - оплачен, 2 - отменён, 3 - ошибка
    amount_usdt = Column(BigInteger, index=True)
    added_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)
    error_message = Column(String)
    invoice_type = Column(Integer, index=True, default=0)


class BotSetting(Base):
    __tablename__ = 'bot_settings'
    id = Column(Integer, primary_key=True, index=True)
    null_view_status_0 = Column(Integer, index=True, default=0)
    null_view_status_1 = Column(Integer, index=True, default=0)
    null_view_status_2 = Column(Integer, index=True, default=0)
    manual_status = Column(Integer, index=True, default=0)
    manual_link = Column(String, index=True)
    added_phones_status = Column(Integer, index=True, default=0)
    get_phones_status = Column(Integer, index=True, default=0)
    proxy_checker_status = Column(Integer, index=True, default=0)
    accounts_checker_status = Column(Integer, index=True, default=0)
    auto_withdraw_status = Column(Integer, index=True, default=0)
    main_drop_calc_amount = Column(Integer, index=True, default=0)
    main_group_calc_amount = Column(Integer, index=True, default=0)
    day_count_sended = Column(Integer, index=True, default=0)
    day_count_added = Column(Integer, index=True, default=0)
    day_limit_sended = Column(Integer, index=True, default=1000)
    day_limit_added = Column(Integer, index=True, default=500)
    limit_queue = Column(Integer, index=True, default=30)
    topic_id = Column(Integer, index=True, default=0)
    topic_applications_theme_id = Column(Integer, index=True, default=0)
    topic_withdraws_theme_id = Column(Integer, index=True, default=0)
    topic_failed_withdraws_theme_id = Column(Integer, index=True, default=0)
    topic_not_found_proxy_theme_id = Column(Integer, index=True, default=0)
    topic_errors_proxy_theme_id = Column(Integer, index=True, default=0)
    topic_errors_theme_id = Column(Integer, index=True, default=0)
    topic_phones_theme_id = Column(Integer, index=True, default=0)
    topic_frozen_theme_id = Column(Integer, index=True, default=0)
    topic_bans_theme_id = Column(Integer, index=True, default=0)
    autoload_proxy_status = Column(Integer, index=True, default=0)
    topic_autoload_proxy = Column(Integer, index=True, default=0)
    proxy_api_token = Column(String, index=True)
    op_group_id = Column(BigInteger, index=True)
    op_group_link = Column(String, index=True)
    auto_kick_group_status = Column(Integer, index=True, default=0)
    rules = Column(String, index=True)
    support_username = Column(String, index=True)
    ref_percent = Column(BigInteger, index=True, default=0)
    deposit_status = Column(Integer, index=True, default=0)
    pay_manual = Column(Integer, index=True, default=0)
    pay_cryptobot = Column(Integer, index=True, default=0)
    usdt_address = Column(String, default='X')
    usdt_waiting = Column(Integer, default=120)
    cryptobot_main_invoice_url = Column(String)
    topic_payments_theme_id = Column(Integer, index=True, default=0)
    topic_cryptobot_payments_theme_id = Column(Integer, index=True, default=0)
    converter_balance_min = Column(BigInteger, index=True, default=0)
    converter_limit_accounts = Column(BigInteger, index=True, default=0)
    converter_account_price = Column(BigInteger, index=True, default=0)
    converter_proxy_api_token = Column(String, index=True)
    converter_valid_price = Column(BigInteger, index=True, default=0)
    pslet_status = Column(Integer, index=True, default=0)
    percent_slet = Column(Integer, index=True, default=0)
    pslet_nevalid_status = Column(Integer, index=True, default=0)
    percent_nevalid = Column(Integer, index=True, default=0)
    op_client_channel_id = Column(BigInteger, index=True)
    op_client_channel_link = Column(String, index=True)

