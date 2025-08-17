from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat
from lexicons.lexicon import LEXICON_COMMANDS_ADM


async def set_main_menu_adm(bot: Bot, chat_id: int = None):
    main_menu_commands = [BotCommand(
        command=comm,
        description=descr) for comm, descr in LEXICON_COMMANDS_ADM.items()
    ]

    await bot.set_my_commands(main_menu_commands, scope=BotCommandScopeChat(chat_id=chat_id))