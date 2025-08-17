import os
import asyncio
from aiogram import Router, F, Bot
from db.main_db import add_media, delete_photos_by_indexes, get_media_by_topic, send_media_in_batches, get_topics
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from filters.filter_admin import AdminFilter
from filters.filter_indx import IndxFilter
from lexicons.lexicon import LEXICON_ADM
from keyboards.admin_inline_kbs import start_kb_adm, manage_db_kb, back_db_kb, topic_kb_db
from aiogram.fsm.context import FSMContext
from FSM.FSM_DB import FSM_DB
from config_data.config import Config, load_config


db_router = Router()

db_router.message.filter(AdminFilter())
db_router.callback_query.filter(AdminFilter())

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Корень проекта
config: Config = load_config(path=os.path.join(base_dir, ".env"))



media_buffer = {}
processing_media_groups = set()


@db_router.message(Command(commands=["manage_db"]))
async def manage_database_comm(message: Message, state: FSMContext):

    await state.set_state(FSM_DB.manage_db)
    await message.answer(text=LEXICON_ADM["manage_database"], reply_markup=manage_db_kb())


@db_router.callback_query(F.data == "/manage_db")
async def manage_database_button(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSM_DB.manage_db)
    await callback.message.edit_text(text=LEXICON_ADM["manage_database"], reply_markup=manage_db_kb())
    await callback.answer()


@db_router.callback_query(lambda callback: callback.data in ("/delete_photo_db", "/show_photo_db", "/add_photo_db"),
                          StateFilter(FSM_DB.manage_db))
async def send_topic(callback: CallbackQuery, state: FSMContext):
    data = callback.data
    topics = await get_topics()
    if not topics and (data == "/delete_photo_db" or data == "/show_photo_db"):
        await callback.message.edit_text(text=LEXICON_ADM["none_topics"], reply_markup=back_db_kb())
        return

    match data:
        case "/add_photo_db":
            await state.set_state(FSM_DB.topic_add_photo)
        case "/show_photo_db":
            await state.set_state(FSM_DB.topic_show)
        case "/delete_photo_db":
            await state.set_state(FSM_DB.topic_del)
        case _:
            await callback.message.answer(text=LEXICON_ADM["error"])
            await state.clear()
            await callback.message.answer(text=LEXICON_ADM["/start"], reply_markup=start_kb_adm())

    text = "<b>\n\nАктуальные темы:\n</b>" + "\n".join(topics) if topics else LEXICON_ADM["examples"]
    if data == "/add_photo_db":
        await callback.message.edit_text(text=LEXICON_ADM["send_topic"] + text)
    else:
        await callback.message.edit_text(text=LEXICON_ADM["send_topic"], reply_markup=topic_kb_db(topics))
    await callback.answer()


@db_router.callback_query(F.data == "back_db")
async def process_back_db_button(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSM_DB.manage_db)
    await callback.message.edit_text(text=LEXICON_ADM["manage_database"], reply_markup=manage_db_kb())
    await callback.answer()


@db_router.message(StateFilter(FSM_DB.topic_add_photo))
async def send_photo(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(text=LEXICON_ADM["none_text"])
        return
    topic = message.text.replace(" ", "")
    await state.update_data(topic=topic)
    await state.set_state(FSM_DB.photo)
    await message.answer(text=LEXICON_ADM["send_photo"])


@db_router.message(StateFilter(FSM_DB.photo))
async def handle_media_album(message: Message, state: FSMContext):
    '''
    Если приходит альбом (media_group_id) то обьекты из альбома берутся поочереди и
    обрабатываются до строчки await asyncio.sleep(1.5) (после того как первый обьект дошел до данной строчки
    мы ждем 1.5с остальные обьекты)

    По итогу media_buffer будет выглядеть так {media_id: [(chat_id, photo1, topic), (chat_id, photo2, topic) ....]}
    '''
    data = await state.get_data()
    topic = data["topic"]
    media_group_id = message.media_group_id
    key = (message.chat.id, media_group_id)

    if media_group_id:
        media_buffer.setdefault(media_group_id, []).append((message.chat.id, message, topic))

        if key in processing_media_groups:
            return
        processing_media_groups.add(key)

        await asyncio.sleep(1.5)

        media_group = media_buffer.pop(media_group_id)
        for chat_id, msg, topic in media_group:
            if msg.photo:
                file_id = msg.photo[-1].file_id
                media_type = "photo"
            elif msg.video:
                file_id = msg.video.file_id
                media_type = "video"
            else:
                continue
            await add_media(file_id, topic, media_type)

        processing_media_groups.remove(key)
        await message.answer(text=LEXICON_ADM["success_add"])
        await state.clear()
        await message.answer(text=LEXICON_ADM["/start"], reply_markup=start_kb_adm())
        return

    if message.photo:
        file_id = message.photo[-1].file_id
        media_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        media_type = "video"
    else:
        await message.answer(text=LEXICON_ADM["photo_video_only"])
        return

    await add_media(file_id, topic, media_type)
    await message.answer(text=LEXICON_ADM["success_add"])
    await state.clear()
    await message.answer(text=LEXICON_ADM["/start"], reply_markup=start_kb_adm())


@db_router.callback_query(StateFilter(FSM_DB.topic_show, FSM_DB.topic_del))
async def show_media(callback: CallbackQuery, state: FSMContext):
    topic = callback.data
    await state.update_data(topic=topic)
    records = await get_media_by_topic(topic)  # [(file_id, media_type)]

    if not records:
        await callback.message.answer(LEXICON_ADM["none_photo"])
        await state.clear()
        await callback.message.answer(text=LEXICON_ADM["/start"], reply_markup=start_kb_adm())
        return

    await send_media_in_batches(callback, records)

    if await state.get_state() == FSM_DB.topic_del:
        await callback.message.answer(LEXICON_ADM["send_indx"])
        await state.set_state(FSM_DB.indx)
    else:
        await callback.message.answer(text=LEXICON_ADM["your_photo"] + topic)
        await state.clear()
        await callback.message.answer(text=LEXICON_ADM["/start"], reply_markup=start_kb_adm())


@db_router.message(StateFilter(FSM_DB.indx), IndxFilter())
async def del_photos(message: Message, state: FSMContext):

    raw_indexes = message.text.split(",")

    indexes = [int(i) - 1 for i in raw_indexes]  # -1, потому что пользователь считает с 1
    data = await state.get_data()
    topic = data["topic"]
    deleted_ids = await delete_photos_by_indexes(topic, indexes)
    await message.answer(text=LEXICON_ADM["succes_del"] + f"<b> {len(deleted_ids)} фото</b>")
    await state.clear()
    await message.answer(text=LEXICON_ADM["/start"], reply_markup=start_kb_adm())


'''
@db_router.channel_post()
async def process_new_post(message: Message, bot: Bot):
    media_group_id = message.media_group_id
    text = message.caption or ""
    chat_id = message.chat.id

    if not media_group_id:
        if not text or "#" not in text:
            for admin_id in config.tg_bot.adm_ids:
                await bot.send_message(chat_id=admin_id, text=LEXICON_ADM["none_#"])
            return

        topic = ""
        for word in text.split():
            if word.startswith("#"):
                topic = word[1:]
                break

        if message.photo:
            file_id = message.photo[-1].file_id
            media_type = "photo"
        elif message.video:
            file_id = message.video.file_id
            media_type = "video"
        else:
            for admin_id in config.tg_bot.adm_ids:
                await bot.send_message(chat_id=admin_id, text=LEXICON_ADM["none_media_channel"])
            return

        await add_media(file_id, topic, media_type)

        for admin_id in config.tg_bot.adm_ids:
            await bot.send_message(chat_id=admin_id, text=LEXICON_ADM["success_add_channel"])
        return

    media_buffer.setdefault(media_group_id, []).append((chat_id, message))

    if media_group_id in processing_media_groups:
        return
    processing_media_groups.add(media_group_id)

    await asyncio.sleep(2.5)

    group_messages = media_buffer.pop(media_group_id, [])
    caption_text = ""

    for _, msg in group_messages:
        if msg.caption and "#" in msg.caption:
            caption_text = msg.caption
            break

    if not caption_text:
        for admin_id in config.tg_bot.adm_ids:
            await bot.send_message(chat_id=admin_id, text=LEXICON_ADM["none_#"])
        processing_media_groups.remove(media_group_id)
        return

    topic = ""
    for word in caption_text.split():
        if word.startswith("#"):
            topic = word[1:]
            break

    for _, msg in group_messages:
        if msg.photo:
            file_id = msg.photo[-1].file_id
            media_type = "photo"
        elif msg.video:
            file_id = msg.video.file_id
            media_type = "video"
        else:
            continue
        await add_media(file_id, topic, media_type)

    for admin_id in config.tg_bot.adm_ids:
        await bot.send_message(chat_id=admin_id, text=LEXICON_ADM["success_add"])

    processing_media_groups.remove(media_group_id)
'''
# если пост в группе то #8марта если просто добавить тему то 8 марта можно

