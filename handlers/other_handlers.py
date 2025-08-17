from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from lexicons.lexicon import LEXICON

router = Router()


@router.message()
async def send_echo_mess(message: Message):
    await message.answer(text=LEXICON["/echo"])


@router.callback_query()
async def send_echo_callback(callback: CallbackQuery):
    await callback.answer(text=LEXICON["/echo"], show_alert=True)

