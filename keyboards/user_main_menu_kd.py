from aiogram import Bot
from aiogram.types import BotCommandScopeChat
from aiogram.types import BotCommand
from lexicons.lexicon import LEXICON_COMMANDS_USER


async def set_main_menu(bot: Bot, chat_id: int = None):
    main_menu_commands = [BotCommand(
        command=comm,
        description=descr) for comm, descr in LEXICON_COMMANDS_USER.items()
    ]
    if chat_id:
        await bot.set_my_commands(main_menu_commands, scope=BotCommandScopeChat(chat_id=chat_id))
    else:
        await bot.set_my_commands(main_menu_commands)

