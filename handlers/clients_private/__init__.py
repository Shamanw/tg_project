from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.types import ChatMemberUpdated, Message
from aiogram.filters import Filter
from aiogram.filters.command import CommandStart, Command
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER, KICKED

from filters.user_type import SecondBot

from .start import router as start_router
from .delete import router as delete_router
from .history import router as history_router
from .deposit import router as deposit_router
from .withdraw import router as withdraw_router
from .convert import router as convert_router
from .catalog import router as catalog_router
from .main import router as main_router

clients_private_router = Router()
clients_private_router.message.filter(SecondBot())
clients_private_router.callback_query.filter(SecondBot())
clients_private_router.message.filter(F.chat.type == ChatType.PRIVATE)
clients_private_router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)
clients_private_router.include_routers(
    start_router,
    delete_router,
    history_router,
    deposit_router,
    withdraw_router,
    convert_router,
    catalog_router,
    main_router,
)
