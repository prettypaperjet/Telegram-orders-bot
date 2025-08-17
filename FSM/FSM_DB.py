from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()


class FSM_DB(StatesGroup):
    manage_db = State()
    topic_del = State()
    topic_show = State()
    topic_add_photo = State()

    photo = State()
    indx = State()

    delete_photo = State()
    show_photo = State()