BOT_TOKEN = '7718920119:AAFMy1sjWYfkHsfeSrcKjht_lfTanPGbi7E'
SECOND_BOT_TOKEN = '7659884337:AAGixlHgFhYwSXEse6lmpWcMFDqFnGscpgg'
ADMIN_ID = 7197907593
#1
from pyrogram import Client

phone_number_main = '380661766553'
pyro_client = Client(
    name=f'sessions/{phone_number_main}',
    api_id=27870989,
    api_hash='a9d328c644f7ab9a35f9a5274b2110f2',
    device_model='iPhone XS',
    system_version='16.6.1',
    app_version='Telegram iOS (27585)',
    lang_code='en',
)

phone_number_second = '380509102754'
pyro_client_second = Client(
    name=f'sessions/{phone_number_second}',
    api_id=29998305,
    api_hash='f4e67f153a5732204b2dd40092850cad',
    device_model='iPhone XS',
    system_version='16.6.1',
    app_version='Telegram iOS (27585)',
    lang_code='en',
)

