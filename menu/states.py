from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class Search(StatesGroup):
    code = State()

class Call_us(StatesGroup):
    tg_dog_link = State()
    text = State()