from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()


class FSMFillForm(StatesGroup):
    fill_topic = State()
    fill_date = State()
    fill_description = State()

