from aiogram.filters import BaseFilter
from aiogram.types import Message
from datetime import datetime
from typing import Union


class IsValidDate(BaseFilter):
    def __init__(self):
        pass

    def validate(self, date_str: str) -> bool:
        if not date_str:
            return False
        try:
            parsed_date = datetime.strptime(date_str, "%d.%m.%Y")
            return parsed_date.year >= 2025
        except ValueError:
            return False

    async def __call__(self, message: Union[Message, str]) -> bool:
        if isinstance(message, Message):
            return self.validate(message.text)
        elif isinstance(message, str):
            return self.validate(message)
        return False
