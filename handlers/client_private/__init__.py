from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.types import ChatMemberUpdated, Message
from aiogram.filters import Filter
from aiogram.filters.command import CommandStart, Command
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER, KICKED

from filters.user_type import RoleFilter

from .start import router as start_router
from .delete import router as delete_router
from .application import router as application_router

client_private_router = Router()
client_private_router.message.filter(RoleFilter(role='client'))
client_private_router.callback_query.filter(RoleFilter(role='client'))
client_private_router.message.filter(F.chat.type == ChatType.PRIVATE)
client_private_router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)
client_private_router.include_routers(
    start_router,
    delete_router,
    application_router,
)
