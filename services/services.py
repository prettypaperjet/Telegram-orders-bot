import os
from aiogram import Bot
import logging
from config_data.config import Config, load_config
from keyboards.user_main_menu_kd import set_main_menu
from keyboards.admin_main_menu_kb import set_main_menu_adm


base_dir = os.path.dirname(os.path.abspath(__file__))
#photos_json_path = os.path.join(base_dir, "photos.json")

config: Config = load_config(path=os.path.join(os.path.dirname(base_dir), ".env"))

logger = logging.getLogger(__name__)


async def setup_comm(bot: Bot, config: Config):
    adm = config.tg_bot.adm_ids

    await set_main_menu(bot)

    # команды для админов
    for admin_id in adm:
        try:
            await set_main_menu_adm(bot, admin_id)
        except Exception:
            logger.error(f"Failed to set admin menu")


def format_order(user_id, user_data):
    return (
            f"<b>{user_data.get('name', 'Не указано')} (id {user_id}):</b>\n"
            f"<i>Username:</i> {user_data.get('username', 'Не указано')}\n"
            f"<i>Тема:</i> {user_data.get('topic', 'Не указано')}\n"
            f"<i>Дата:</i> {user_data.get('date', 'Не указано')}\n"
            f"<i>Описание:</i> <code>{user_data.get('description', 'Не указано')}</code>"
    )


def format_mess(user_id, user_data):
    return (
        f"<b>{user_data['name']} (id {user_id}):</b>\n\n"
        f"{user_data['topic']}\n"
    )
