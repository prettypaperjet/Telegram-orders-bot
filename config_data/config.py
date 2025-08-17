from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str
    adm_ids: list[int]
    channel_username: str
    bot_chat_id: int
    DATABASE_ID_NOTION: str
    NOTION_TOKEN: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    POSTGRES_PASSWORD: int
    DB_NAME: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env("BOT_TOKEN"),
            adm_ids=list(map(int, env.list("ADM_IDS"))),
            channel_username=env("CHANNEL_USERNAME"),
            bot_chat_id=int(env("BOT_CHAT_ID")),
            DATABASE_ID_NOTION=env("DATABASE_ID_NOTION"),
            NOTION_TOKEN=env("NOTION_TOKEN"),
            DB_HOST=env("DB_HOST"),
            DB_PORT=env("DB_PORT"),
            DB_USER=env("DB_USER"),
            POSTGRES_PASSWORD=env("POSTGRES_PASSWORD"),
            DB_NAME=env("DB_NAME")
        )
    )
