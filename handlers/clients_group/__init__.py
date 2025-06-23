from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.types import ChatMemberUpdated, Message
from aiogram.filters import Filter
from aiogram.filters.command import CommandStart, Command
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER, KICKED

from filters.user_type import RoleFilter, GroupFilter, SecondBot

from .start import router as start_router
from .delete import router as delete_router
from .catalog import router as catalog_router

clients_group_router = Router()
clients_group_router.message.filter(SecondBot())
clients_group_router.callback_query.filter(SecondBot())
clients_group_router.message.filter(F.chat.type == ChatType.SUPERGROUP or F.chat.type == ChatType.GROUP)
clients_group_router.callback_query.filter(F.message.chat.type == ChatType.SUPERGROUP or F.chat.type == ChatType.GROUP)
clients_group_router.include_routers(
    start_router,
    delete_router,
    catalog_router,
)
