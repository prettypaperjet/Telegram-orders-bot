import logging
import os
import asyncpg
from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from typing import Optional, List
from aiogram.types import InputMediaPhoto, InputMediaVideo
from config_data.config import load_config, Config


logger = logging.getLogger(__name__)

pool: Optional[asyncpg.pool.Pool] = None

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config: Config = load_config(path=os.path.join(base_dir, ".env"))


async def connect_to_db():
    global pool

    # Data Source Name
    dsn = (f"postgresql://{config.tg_bot.DB_USER}:{config.tg_bot.POSTGRES_PASSWORD}@{config.tg_bot.DB_HOST}:{config.tg_bot.DB_PORT}/"
           f"{config.tg_bot.DB_NAME}")

    pool = await asyncpg.create_pool(dsn=dsn)


async def close_db():
    # Закрываем пул соединений с базой данных
    await pool.close()


# Создание таблицы для хранения фото
async def create_table():
    async with pool.acquire() as connection: # берём одно соединение из пула
        # выполняем SQL запрос на создание таблицы
        await connection.execute(''' 
            CREATE TABLE IF NOT EXISTS media (
                id SERIAL PRIMARY KEY,
                file_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                media_type TEXT DEFAULT 'photo'
            )
        ''')


async def send_media_in_batches(event: CallbackQuery | Message, media_list: List[tuple], bot: Bot = False):
    mess = isinstance(event, Message)
    BATCH_SIZE = 10

    for i in range(0, len(media_list), BATCH_SIZE):
        batch = media_list[i:i + BATCH_SIZE] # media_list[0:9], media_list[10:19]
        # print(f"Отправляем batch из {len(batch)} медиа")
        media = []

        # рпоходимся по альбому
        for file_id, media_type in batch:
            if media_type == "photo":
                media.append(InputMediaPhoto(media=file_id))
            elif media_type == "video":
                media.append(InputMediaVideo(media=file_id))

        if not media:
            continue

        chat_id = event.chat.id if mess else event.message.chat.id
        try:
            if bot:
                if len(media) == 1:
                    if isinstance(media[0], InputMediaPhoto):
                        await bot.send_photo(chat_id, photo=media[0].media)
                    else:
                        await bot.send_video(chat_id, video=media[0].media)
                else:
                    await bot.send_media_group(chat_id=chat_id, media=media)
            else:
                if len(media) == 1:
                    if isinstance(media[0], InputMediaPhoto):
                        await event.answer_photo(media[0].media) if mess else await event.message.answer_photo(media[0].media)
                    else:
                        await event.answer_video(media[0].media) if mess else await event.message.answer_video(media[0].media)
                else:
                    await event.answer_media_group(media) if mess else await event.message.answer_media_group(media)
        except Exception as e:
            logger.error(e)
            # print(f"file_ids: {batch}")


async def add_media(file_id: str, topic: str, media_type: str):
    async with pool.acquire() as connection:
        await connection.execute('''
            INSERT INTO media (file_id, topic, media_type) VALUES ($1, $2, $3)
        ''', file_id, topic, media_type)


async def get_media_by_topic(topic: str) -> List[tuple[str, str]]:
    async with pool.acquire() as connection:
        records = await connection.fetch('''
            SELECT file_id, media_type FROM media WHERE topic = $1
        ''', topic)
        return [(r['file_id'], r['media_type']) for r in records]


async def get_topics() -> List[str]:
    async with pool.acquire() as connection:
        rows = await connection.fetch('''
            SELECT DISTINCT topic FROM media
            ''')
        return [row["topic"] for row in rows]


async def delete_photos_by_indexes(topic: str, indexes: list[int]) -> list[str]:
    async with pool.acquire() as connection:
        # Получаем все file_id по теме, отсортированные по времени
        rows = await connection.fetch('''
            SELECT file_id FROM media WHERE topic = $1 ORDER BY added_at
        ''', topic)

        valid_file_ids = [rows[i]['file_id'] for i in indexes if 0 <= i < len(rows)]

        if not valid_file_ids:
            return []

        # $1::text[] это передача массива строк как SQL массива типа text[]
        # ANY() означает что file_id должен быть одним из элементов массива
        await connection.execute('''
            DELETE FROM media WHERE file_id = ANY($1::text[])
        ''', valid_file_ids)

        return valid_file_ids