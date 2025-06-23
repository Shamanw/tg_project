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

