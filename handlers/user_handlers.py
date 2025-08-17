import os
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
from lexicons.lexicon import LEXICON, LEXICON_ADM
from keyboards.user_inline_kds import start_kb, back_kb, topic_kb
from db.main_db import get_topics
from keyboards.admin_inline_kbs import reply_new_order
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from FSM.FSMFillForm import FSMFillForm
from filters.filter_date import IsValidDate
from db.local_db import users
from filters.filter_admin import AdminFilter
from config_data.config import load_config, Config


router = Router()

router.message.filter(~AdminFilter())
router.callback_query.filter(~AdminFilter())
#os.path.abspath(__file__) абсолютный путь к текущему файлу
    #os.path.dirname(path) путь к папке
    #второй os.path.dirname() поднимает нас в корневую папку проекта
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Корень проекта
config: Config = load_config(path=os.path.join(base_dir, ".env"))


@router.message(CommandStart())
async def process_start_comm(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(LEXICON[message.text],
                         reply_markup=start_kb("order", "help", "about"))


@router.message(Command(commands=["help"]))
async def process_help_comm(message: Message):
    await message.answer(LEXICON[message.text])


@router.callback_query(F.data == "/help")
async def process_help_button(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON[callback.data], reply_markup=back_kb())
    await callback.answer()


@router.message(Command(commands=["about"]))
async def process_about_comm(message: Message):
    await message.answer(LEXICON[message.text])


@router.callback_query(F.data == "/about")
async def process_about_button(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON[callback.data], reply_markup=back_kb())
    await callback.answer()


@router.callback_query(F.data == "/back")
async def process_back_button(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON["/start"], reply_markup=start_kb("order", "help", "about"))
    await callback.answer()


@router.callback_query(F.data == "/order", StateFilter(default_state))
async def process_order_button(callback: CallbackQuery, state: FSMContext):
    await state.update_data(name=callback.from_user.first_name)
    topics = await get_topics()
    await callback.message.edit_text(text=LEXICON["/choose_topic"], reply_markup=topic_kb(topics))
    await state.set_state(FSMFillForm.fill_topic)


@router.message(Command(commands=["order"]), StateFilter(default_state))
async def process_name_user(message: Message, state: FSMContext):
    await state.update_data(name=message.from_user.first_name)
    topics = await get_topics()
    await message.answer(text=LEXICON["/choose_topic"], reply_markup=topic_kb(topics))
    await state.set_state(FSMFillForm.fill_topic)


@router.callback_query(StateFilter(FSMFillForm.fill_topic))
async def process_topic_button(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(topic=callback.data)
    await callback.message.edit_text(text=LEXICON["fill_date"])
    await state.set_state(FSMFillForm.fill_date)


@router.message(StateFilter(FSMFillForm.fill_date), IsValidDate())
async def process_date_button(message: Message, state: FSMContext):
    try:
        # ISO формат2025-05-31
        parsed_date = datetime.strptime(message.text, "%d.%m.%Y").date().isoformat()
    except ValueError:
        await message.answer("⚠️ Неверный формат даты. Введите в формате ДД.ММ.ГГГГ, например 31.05.2025")
        return

    await state.update_data(date=parsed_date)
    await message.answer(text=LEXICON["fill_description"], input_field_placeholder="Введите описание ⬅️")
    await state.set_state(FSMFillForm.fill_description)


@router.message(StateFilter(FSMFillForm.fill_description))
async def process_description_update(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(description=message.text)
    await message.answer(text=LEXICON["end"])
    users[message.from_user.id] = await state.get_data()
    users[message.from_user.id]["username"] = "@" + message.from_user.username
    await state.clear()
    for admin_id in config.tg_bot.adm_ids:
        await bot.send_message(chat_id=admin_id, text=LEXICON_ADM["new_order"], reply_markup=reply_new_order())
