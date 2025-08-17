from aiogram.filters import BaseFilter
from aiogram.types import Message


class IndxFilter(BaseFilter):
    async def __call__(self, message: Message):
        for st in message.text.split():
            if st.isalpha():
                return False
        return True


