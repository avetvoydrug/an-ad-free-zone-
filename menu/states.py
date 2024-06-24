from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class Search(StatesGroup):
    code = State()

class Call_us(StatesGroup):
    tg_dog_link = State()
    text = State()

####################ADMIN_STATES#####################
class Video_id(StatesGroup):
    video = State()

class Film(StatesGroup):
    code = State()
    name = State()

class Serie(StatesGroup):
    code = State()
    season = State()
    part = State()
    tg_file_id = State()

class MakeAdmin(StatesGroup):
    tg_id = State()

class GetSerie(StatesGroup):
    films_id = State()
    season = State()
    part = State()

class DeleteSerie(StatesGroup):
    serie_id = State()

class DeleteFilm(StatesGroup):
    films_id = State()

class UpdateFilm(StatesGroup):
    films_id = State()
    name = State()

class SendMail(StatesGroup):
    text = State()
