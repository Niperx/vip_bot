from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from modules.admins_list import ADMINS


class IsAdmin(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        if message.from_user.is_bot == True or message.from_user.first_name == 'Group' or message.from_user.id in ADMINS:
            return True


class IsPrivate(BoundFilter):
    key = 'is_private'

    def __init__(self, is_private):
        self.is_private = is_private

    async def check(self, message: types.Message):
        if message.chat.type == 'private':
            return True
