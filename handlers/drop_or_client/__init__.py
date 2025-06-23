from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.types import ChatMemberUpdated, Message
from aiogram.filters.command import CommandStart, Command
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER, KICKED

from filters.user_type import RoleFilter

from .delete import router as delete_router
from .slet_phones import router as slet_phones_router
from .unban import router as unban_router

drop_or_client_router = Router()
drop_or_client_router.message.filter(F.chat.type == ChatType.PRIVATE)
drop_or_client_router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)
drop_or_client_router.include_routers(
    delete_router,
    slet_phones_router,
    unban_router,
)

