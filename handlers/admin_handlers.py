import os
import requests
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
from handlers.db_handlers import db_router
from filters.filter_admin import AdminFilter
from filters.filter_date import IsValidDate
from lexicons.lexicon import LEXICON_ADM
from keyboards.admin_inline_kbs import (start_kb_adm, orders_kb_comm, orders_kb_choose, back_kb_adm, choose_change_ord,
                                        choose_change_data)
from db.local_db import users
from aiogram.fsm.context import FSMContext
from FSM.FSMConfirmOrder import FSMConfirmOrder
from config_data.config import Config, load_config
from services.services import format_order


adm_router = Router()
adm_router.include_router(db_router)

adm_router.message.filter(AdminFilter())
adm_router.callback_query.filter(AdminFilter())

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config: Config = load_config(path=os.path.join(base_dir, ".env"))


@adm_router.message(CommandStart())
async def process_start_command_adm(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=LEXICON_ADM[message.text], reply_markup=start_kb_adm())


@adm_router.callback_query(F.data == "/help")
async def process_help_button_adm(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON_ADM[callback.data], reply_markup=back_kb_adm())
    await callback.answer()


@adm_router.callback_query(F.data == "back")
async def process_back_button_adm(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON_ADM["/start"], reply_markup=start_kb_adm())
    await callback.answer()


@adm_router.message(Command(commands=["help"]))
async def process_help_comm_adm(message: Message):
    await message.answer(text=LEXICON_ADM[message.text])


@adm_router.message(Command(commands=["show_orders_adm"]))
@adm_router.message(Command(commands=["confirm_order"]))
async def process_look_orders_button(message: Message, state: FSMContext):
    """
            - Обработчик комманд '/show_orders_adm' и '/confirm_order'
            - После проверки на наличие заказов присылает список всех заказов (LEXICON_ADM[message.text])
            и предлагает выбрать один из них (orders_kb)
            - Если обрабатывает комманду '/confirm_order', то ставит состояние выбор заказа
            для подтверждения (choose_confirm_order)
    """
    if not users:
        await message.answer(text=LEXICON_ADM["not_users"])
    else:
        await message.answer(text=f"<b>Актуальные заказы</b>\n\n\n" +
                                  "\n\n\n".join(format_order(user_id, data) for user_id, data in users.items()) +
                                  f"<b>\n\n\nВыберите пользователя:</b>",
                             reply_markup=orders_kb_comm(users) if message.text == "/show_orders_adm"
                             else orders_kb_choose(users))

        if message.text == "/confirm_order":
            await state.set_state(FSMConfirmOrder.choose_confirm_order)


@adm_router.callback_query(F.data == "/show_orders_adm")
async def process_look_orders_button(callback: CallbackQuery):
    if not users:
        await callback.message.edit_text(text=LEXICON_ADM["not_users"], reply_markup=back_kb_adm())
    else:
        await callback.message.edit_text(text=f"<b>Актуальные заказы</b>\n\n\n" +
                                              "\n\n\n".join(format_order(user_id, data) for user_id, data in users.items()) +
                                         f"<b>\n\n\n\nВыберите пользователя:</b>",
                                         reply_markup=orders_kb_comm(users))
    await callback.answer()


@adm_router.callback_query(StateFilter(FSMConfirmOrder.choose_confirm_order))
async def process_choose_change_order(callback: CallbackQuery, state: FSMContext):
    """
            - Обработчик выбора заказа администратора
            - Заносит id пользователя в FSMContext
            - Предлагает изменить данные заказа
    """
    user_id = int(callback.data.strip("order_"))
    await state.update_data(user_id=user_id)
    await callback.message.edit_text(text=LEXICON_ADM["choose_change_order"], reply_markup=choose_change_ord())
    await state.set_state(FSMConfirmOrder.choose_change_order)
    await callback.answer()


@adm_router.callback_query(StateFilter(FSMConfirmOrder.change_data), F.data == "/yes")
@adm_router.callback_query(StateFilter(FSMConfirmOrder.choose_change_order), F.data == "/yes")
async def process_change_order(callback: CallbackQuery, state: FSMContext):
    """
        - Обработчик подтверждения изменения заказа
        - Получает ID пользователя из FSMContext
        - Если админ только что выбрал заказ (`choose_change_order`),
        предлагает выбрать конкретные данные для изменения.
        - Если админ уже поменял данные (`change_data`) и выбрал еще что-то менять,
        обработчик снова предлагает выбрать, что именно изменить
    """
    data = await state.get_data()
    user_id = data.get("user_id")

    await callback.message.edit_text(text=f"{LEXICON_ADM['change_order']} {users[user_id]['name']} ({user_id})",
                                     reply_markup=choose_change_data())

    if await state.get_state() == FSMConfirmOrder.choose_change_order.state:
        await state.set_state(FSMConfirmOrder.change_data)
    await callback.answer()


@adm_router.callback_query(StateFilter(FSMConfirmOrder.change_data))
async def process_new_data(callback: CallbackQuery, state: FSMContext):
    if callback.data == "change_name":
        await callback.message.edit_text(text=LEXICON_ADM["change_name"])
        await state.set_state(FSMConfirmOrder.change_name)
    elif callback.data == "change_descr":
        await callback.message.edit_text(text=LEXICON_ADM["change_descr"])
        await state.set_state(FSMConfirmOrder.change_descr)
    elif callback.data == "change_date":
        await callback.message.edit_text(text=LEXICON_ADM["change_date"])
        await state.set_state(FSMConfirmOrder.change_date)
    await callback.answer()


@adm_router.message(StateFilter(FSMConfirmOrder.change_name))
@adm_router.message(StateFilter(FSMConfirmOrder.change_descr))
@adm_router.message(StateFilter(FSMConfirmOrder.change_date))
async def process_new_data_in_db(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]
    current_state = await state.get_state()

    match current_state:
        case FSMConfirmOrder.change_name.state:
            users[user_id]["name"] = message.text

        case FSMConfirmOrder.change_descr.state:
            users[user_id]["description"] = message.text

        case FSMConfirmOrder.change_date.state:
            validator = IsValidDate()
            if not validator.validate(message.text):
                await message.answer(text=LEXICON_ADM["error_date"])
                return

            try:
                # Преобразуем в ISO-формат: 2025-05-31
                parsed_date = datetime.strptime(message.text, "%d.%m.%Y").date().isoformat()
            except ValueError:
                await message.answer(text=LEXICON_ADM["error_date"])
                return
            users[user_id]["date"] = parsed_date

    await state.set_state(FSMConfirmOrder.choose_change_order)
    await message.answer(text=LEXICON_ADM["new_data"], reply_markup=choose_change_ord())


@adm_router.callback_query(StateFilter(FSMConfirmOrder.change_data), F.data == "/no")
@adm_router.callback_query(StateFilter(FSMConfirmOrder.choose_change_order), F.data == "/no")
async def make_name_task(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=LEXICON_ADM["name_task"])
    await state.set_state(FSMConfirmOrder.name_of_task)
    await callback.answer()


@adm_router.message(StateFilter(FSMConfirmOrder.name_of_task))
async def process_confirm_order(message: Message, state: FSMContext):
    """
            - Обработчик для отправки данных в Notion
    """
    await state.update_data(name_task=message.text)
    data = await state.get_data()

    if "user_id" not in data:
        await message.answer(LEXICON_ADM["user_not_found"])
        return

    user_id = data["user_id"]

    if user_id not in users:
        await message.answer(LEXICON_ADM["user_not_found"])
        return

    user_data = users[user_id]
    iso_date = user_data["date"]  # уже ISO-строка

    if user_id in users:
        users.pop(user_id, None)

    DATABASE_ID = config.tg_bot.DATABASE_ID_NOTION
    NOTION_TOKEN = config.tg_bot.NOTION_TOKEN

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }


    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Название заказа (имя заказчика)": {
                "title": [
                    {
                        "text": {
                            "content": f"{data['name_task']} ({user_data['name']})"
                        }
                    }
                ]
            },
            "Тип заказа": {
                "multi_select": [
                    {"name": "Фотозона"}
                ]
            },
            "Описание": {
                "rich_text": [
                    {"text": {"content": user_data["description"]}}
                ]
            },
            "Дэдлайн": {
                "date": {
                    "start": iso_date
                }
            }
        }
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)

    if response.status_code in (200, 201):
        await message.answer(text=LEXICON_ADM["/no"])
        await state.clear()
        await message.answer(text=LEXICON_ADM["/start"], reply_markup=start_kb_adm())
    else:
        await message.answer(LEXICON_ADM["error_notion"] + f"\n{response.text}")


