from typing import Union, Type, List

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, KeyboardButton


class InvalidKeyboardType(Exception):
    pass


class InvalidButtonType(InvalidKeyboardType):
    pass


class KeyboardBuilder:
    def __init__(
            self: "KeyboardBuilder",
            btn_class: Union[
                Type[InlineKeyboardMarkup],
                Type[ReplyKeyboardMarkup]
            ] = None,
            row_width: int = 3,
            base_keyboard: Union[
                List[List[InlineKeyboardButton]],
                List[List[KeyboardButton]],
                InlineKeyboardMarkup,
                ReplyKeyboardMarkup
            ] = None
    ):
        if not btn_class:
            btn_type = type(base_keyboard)
            if btn_type in [InlineKeyboardMarkup, ReplyKeyboardMarkup]:
                self.btn_class = btn_type
            else:
                raise InvalidKeyboardType
        else:
            self.btn_class = btn_class

        if isinstance(base_keyboard, InlineKeyboardMarkup):
            self.keyboard = base_keyboard.inline_keyboard
        elif isinstance(base_keyboard, ReplyKeyboardMarkup):
            self.keyboard = base_keyboard.keyboard
        else:
            self.keyboard = base_keyboard or []
        self.row_width = row_width

    def as_markup(self, **kwargs):
        if not hasattr(self.btn_class, '__name__'):
            raise InvalidKeyboardType

        if self.btn_class.__name__ == 'InlineKeyboardMarkup':
            return self.btn_class(inline_keyboard=self.keyboard)

        elif self.btn_class.__name__ == 'ReplyKeyboardMarkup':
            resize_keyboard = True
            if 'resize_keyboard' in kwargs:
                if not kwargs['resize_keyboard']:
                    resize_keyboard = False
                else:
                    del kwargs['resize_keyboard']
            return self.btn_class(
                keyboard=self.keyboard,
                resize_keyboard=resize_keyboard,
                **kwargs
            )
        raise InvalidKeyboardType

    def add(self, *buttons):
        row = []
        for index, button in enumerate(buttons, start=1):
            if type(button) not in [InlineKeyboardButton, KeyboardButton]:
                raise InvalidButtonType
            row.append(button)
            if index % self.row_width == 0:
                self.keyboard.append(row)
                row = []
        if row:
            self.keyboard.append(row)
        return self

    def row(self, *buttons):
        btn_array = [btn for btn in buttons]
        self.keyboard.append(btn_array)
        return self

    def insert(self, button):
        if self.keyboard and len(self.keyboard[-1]) < self.row_width:
            self.keyboard[-1].append(button)
        else:
            self.add(button)
        return self
