import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config_data.config import Config, load_config
from handlers import user_handlers, admin_handlers, other_handlers
from db.main_db import connect_to_db, close_db, create_table

from keyboards.user_main_menu_kd import set_main_menu
from keyboards.admin_main_menu_kb import set_main_menu_adm

from services.services import setup_comm


logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    config: Config = load_config()

    await connect_to_db()
    await create_table()


    bot = Bot(token=config.tg_bot.token,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()

    await setup_comm(bot, config)


    dp.include_router(admin_handlers.adm_router)
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    await close_db()

asyncio.run(main())
