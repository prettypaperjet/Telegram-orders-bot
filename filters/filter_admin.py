import os
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from config_data.config import load_config, Config

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Корень проекта
config: Config = load_config(path=os.path.join(base_dir, ".env"))


class AdminFilter(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery):
        return event.from_user.id in config.tg_bot.adm_ids
