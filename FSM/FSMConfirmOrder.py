from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()


class FSMConfirmOrder(StatesGroup):
    choose_confirm_order = State()
    choose_change_order = State()
    change_data = State()
    change_name = State()
    change_descr = State()
    change_date = State()
    name_of_task = State()

