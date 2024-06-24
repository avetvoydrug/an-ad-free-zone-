import os
from dotenv import load_dotenv
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ContentType, CallbackQuery

from aiogram.fsm.context import FSMContext
from menu.states import (Search, Call_us, Video_id, 
                         Film, Serie, MakeAdmin, GetSerie,
                         DeleteSerie, DeleteFilm, UpdateFilm,
                         SendMail)

import menu.keyboards as kb
from menu.tg_api import is_sub
from menu.database.requests import (get_film, get_series, check_status, 
                                    set_film, set_serie, set_user, set_admin,
                                    get_last_film_code, get_some_serie, delete_serie,
                                    delete_film, update_film, get_users)
from menu.middlewares import AntiSpamMiddleware

router = Router()
load_dotenv()
router.message.middleware(AntiSpamMiddleware(limit=2, cooldown=5))


@router.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id)
    #припилить видос с гайдом к приветственному месседжу
    await message.answer('Приветствуем Вас в зоне без рекламы ;)', reply_markup=kb.main)

####################ADMIN_HANDLERS#####################


@router.message(Command('admin'))
async def cmd_admin(message: Message):
    user = await check_status(message.from_user.id)
    if user:
        await message.answer('Что делаем?', reply_markup=kb.admin)
    else:
        await message.delete()
        await message.answer('Отказано в доступе')

#@?! Узнать file_id
@router.callback_query(F.data == 'file_id_admin')
async def video_file_id(callback: CallbackQuery, state: FSMContext):
    #await message.answer_video(video='BAACAgIAAxkBAAMFZnGkOIqtILTirBkC4DfANzRumyAAAsFQAAOqkEtfGbJo6xg7sDUE')
    #await message.answer(message.video.file_id)
    await state.set_state(Video_id.video)
    await callback.message.answer('дропните мувик')

@router.message(Video_id.video)
async def video_file_id_get(message: Message, state: FSMContext):
    await state.update_data(video=message.video.file_id)
    data = await state.get_data()
    await message.answer(f'{data["video"]}')
    await state.clear()

#@?! Добавить новый фильм/сериал
@router.callback_query(F.data == 'add_new_admin')
async def set_new_film(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Film.code)
    await callback.message.answer('Установите уникальный код')

@router.message(Film.code)
async def set_new_film_name(message: Message, state: FSMContext):
    await state.update_data(code=message.text)
    await state.set_state(Film.name)
    await message.answer('Установите название для фильма/сериала')

@router.message(Film.name)
async def set_new_film_upload(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    try:
        await set_film(int(data["code"]), data["name"])
        await message.answer(f'Успешно добавлен\ncode: {data["code"]}\nНазвание: {data["name"]}')
        await state.clear()
    except Exception:
        await message.answer(f'Похоже, что этот код уже занят\ncode: {data["code"]}')
        await state.clear()

#@?! Добавить к существующим
@router.callback_query(F.data == 'add_admin')
async def set_new_serie(callback: CallbackQuery, state: FSMContext): 
    await state.set_state(Serie.code)
    await callback.message.answer('Введите существующий уникальный код')

@router.message(Serie.code)
async def set_serie_season(message: Message, state: FSMContext):
    await state.update_data(code=message.text)
    await state.set_state(Serie.season)
    await message.answer('Введите номер сезона')

@router.message(Serie.season)
async def set_serie_part(message: Message, state: FSMContext):
    await state.update_data(season=message.text)
    await state.set_state(Serie.part)
    await message.answer('Введите номер серии')

@router.message(Serie.part)
async def set_serie_file_id(message: Message, state: FSMContext):
    await state.update_data(part=message.text)
    await state.set_state(Serie.tg_file_id)
    await message.answer('Past file_id')

@router.message(Serie.tg_file_id)
async def set_serie_final(message: Message, state: FSMContext):
    await state.update_data(tg_file_id=message.text)
    data = await state.get_data()
    await set_serie(int(data["code"]), int(data["season"]), int(data["part"]), data["tg_file_id"])
        #await message.answer(f'Что-то не так')
        #await state.clear()
    await message.answer(f'Успешно добавлен\ncode: {data["code"]}\nseason: {data["season"]}\npart: {data["part"]}\nfile_id: {data["tg_file_id"]}')
    await state.clear()

#$?! set_admin
@router.callback_query(F.data == 'set_admin')
async def set_new_admin_tg_id(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MakeAdmin.tg_id)
    await callback.message.answer('Введите tg_id нового админа')

@router.message(MakeAdmin.tg_id)
async def set_new_admin(message: Message, state: FSMContext):
    await state.update_data(tg_id=message.text)
    data = await state.get_data()
    await set_admin(int(data["tg_id"]))
    from main import bot
    user = await bot.get_chat(int(data["tg_id"]))
    await message.answer(f'Успешно выданы права админа: @{user.username}\n id: {data["tg_id"]}')
    await state.clear()

#@?! Получить последний код
@router.callback_query(F.data == 'get_code_admin')
async def get_last_code(callback: CallbackQuery):
    code = await get_last_film_code()
    await callback.message.answer(f'Последний добавленный фильм по коду: {code}')

#@?! Получить код серии
@router.callback_query(F.data == 'get_code_serie_admin')
async def get_code_serie_first(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GetSerie.films_id)
    await callback.message.answer('Введите films_id')

@router.message(GetSerie.films_id)
async def get_code_serie_films_id(message: Message, state: FSMContext):
    await state.update_data(films_id=message.text)
    await state.set_state(GetSerie.season)
    await message.answer('Введите номер сезона')

@router.message(GetSerie.season)
async def get_code_serie_season(message: Message, state: FSMContext):
    await state.update_data(season=message.text)
    await state.set_state(GetSerie.part)
    await message.answer('Введите номер серии')

@router.message(GetSerie.part)
async def get_code_serie(message: Message, state: FSMContext):
    await state.update_data(part=message.text)
    data = await state.get_data()
    codes = await get_some_serie(int(data["films_id"]), int(data["season"]), int(data["part"]))
    ids = [code.id for code in codes]
    await message.answer(f'Код(ы) серий: {ids}')
    await state.clear()

#@?! Удалить серию
@router.callback_query(F.data == 'delete_admin')
async def delete_serie_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DeleteSerie.serie_id)
    await callback.message.answer('Введите код серии')

@router.message(DeleteSerie.serie_id)
async def delete_serie_finally(message: Message, state: FSMContext):
    await state.update_data(serie_id=message.text)
    data = await state.get_data()
    await delete_serie(int(data["serie_id"]))
    await message.answer('Серия успешно удалена')
    await state.clear()

#@?! Удалить полностью
@router.callback_query(F.data == 'delete_full_admin')
async def delete_film_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DeleteFilm.films_id)
    await callback.message.answer('Введите films_id')

@router.message(DeleteFilm.films_id)
async def delete_film_finally(message: Message, state: FSMContext):
    await state.update_data(films_id=message.text)
    data = await state.get_data()
    await delete_film(int(data["films_id"]))
    await message.answer('Этой ленты больше нет')
    await state.clear()

#@?! Исправить название фильма
@router.callback_query(F.data == 'change_film_admin')
async def update_film_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UpdateFilm.films_id)
    await callback.message.answer('Введите films_id')

@router.message(UpdateFilm.films_id)
async def update_film_name(message: Message, state: FSMContext):
    await state.update_data(films_id=message.text)
    await state.set_state(UpdateFilm.name)
    await message.answer('Введите новое название')

@router.message(UpdateFilm.name)
async def update_film_finally(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await update_film(int(data["films_id"]), data["name"])
    await message.answer(f'Новое название:\n{data["name"]}')
    await state.clear()

#@?! Отправить рассылку
@router.callback_query(F.data == 'send_admin')
async def send_mails(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SendMail.text)
    await callback.message.answer('наберите сообщение для рассылки')

@router.message(SendMail.text)
async def send_mails_finally(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    users = await get_users()
    from main import bot
    for user in users:
        await bot.send_message(chat_id=user.tg_id, text=data["text"])
    await state.clear()

####################ANY_HANDLERS#####################        


@router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery):
    await callback.message.edit_text('Приветствуем Вас в зоне без рекламы ;)', reply_markup=kb.main)

@router.callback_query(F.data == 'to_main_wo_edit')
async def to_main(callback: CallbackQuery):
    await callback.message.answer('Приветствуем Вас в зоне без рекламы ;)', reply_markup=kb.main)

@router.message(F.content_type == ContentType.VIDEO)
async def video_file(message: Message):
    await message.answer(message.video.file_id)

####################FIND_FILMS_HANDLERS#####################        


@router.callback_query(F.data == 'find_films')
async def movie_finder_first_step(callback: CallbackQuery, state: FSMContext):
    st = await is_sub(callback.from_user.id)
    if st:
        await state.set_state(Search.code)
        await callback.message.edit_text(
            text='input films code'
        )
    else:
        await callback.message.edit_text(
            text='u need to sub a channel',
            reply_markup= await kb.subscriptions()
        )

@router.message(Search.code)
async def search(message: Message, state: FSMContext):
    st = await is_sub(message.from_user.id)
    if st:
        await state.update_data(code=message.text)
        data = await state.get_data()
        try:
            code_film = int(data["code"])
            if code_film > 0 and code_film < 10000:
                film = await get_film(code_film)
                series = await get_series(code_film)
                if film and series:
                    first = series.first()
                    await message.answer_video(
                        video=f'{first.tg_file_id}',
                        caption=f'Вы смотрите {film.name}',
                        reply_markup= await kb.series(code_film)
                        )
                else:
                    await state.clear()
                    await state.set_state(Search.code)
                    await message.answer('Такого кода не существует\nВведите корректно ;)')
            else:
                await state.clear()
                await state.set_state(Search.code)
                await message.answer('Такого кода не существует\nВведите корректно ;)')
        except Exception:
            await message.answer(f'{message.from_user.first_name}, код должен состоять только из цифр\nВы ввели: {data["code"]}\nПовторите ввод корректно :)')
            await state.clear()
            await state.set_state(Search.code)
            print(f'Дебил пытался наебать систему')
    else:
        message.answer(
            text='u need to sub a channel :)',
            reply_markup= await kb.subscriptions()
        )

@router.callback_query(F.data.startswith('season_'))
async def next_serie(callback: CallbackQuery):
    st = await is_sub(callback.from_user.id)
    if st:
        # 'season_{code}_{serie.season}_{serie.part}'
        data = callback.data.split('_')
        film = await get_film(int(data[1]))
        series = await get_series(int(data[1]))
        target_serie = next(
            (s for s in series if s.season == int(data[2]) and s.part == int(data[3])), 
            None)
        await callback.message.answer_video(
            video=f'{target_serie.tg_file_id}',
            caption=f'Вы смотрите {film.name}',
            reply_markup= await kb.series(int(data[1]))
        )
    else:
        # zatestit
        await callback.message.answer(
            text='u need to sub a channel :)',
            reply_markup= await kb.subscriptions()
        )

####################ADS_HANDLERS#####################

@router.callback_query(F.data.in_({'ads', 'change'}))
async def call(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Call_us.tg_dog_link)
    await callback.message.answer('Выберите контакт для связи, с помощью кнопки', reply_markup= kb.send_link)

@router.message(Call_us.tg_dog_link)
async def call_text(message:Message, state: FSMContext):
    await state.update_data(tg_dog_link=message.user_shared)
    await state.set_state(Call_us.text)
    await message.answer('Введите текст Вашего сообщения')
    
@router.message(Call_us.text)
async def call_check(message: Message, state: FSMContext):
    from main import bot
    await state.update_data(text=message.text)
    data = await state.get_data()
    user = data["tg_dog_link"]
    username = await bot.get_chat(int(user.user_id))
    await message.answer(f'Вот, что Вы ввели:\nАккаунт для связи: @{username.username}\nТекст сообщения: {data["text"]}')
    await message.answer('Если всё верно нажмите отправить', reply_markup= kb.approve)

@router.callback_query(F.data == 'approve')
async def call_end(callback: CallbackQuery, state: FSMContext):
    from main import bot
    data = await state.get_data()
    user = data["tg_dog_link"]
    username = await bot.get_chat(int(user.user_id))
    # TG_ID - id админа или прочих
    await bot.send_message(
        chat_id=int(os.getenv('TG_ID')),
        text=f'@{username.username}\n{data["text"]}')
    await callback.message.edit_text(
        text='Ваше сообщение успешно отправлено\nОжидайте обратной связи',
        reply_markup= kb.to_main
    )
####################SPAM_HANDLER#####################        

@router.message(F.content_type.in_(
        {
            ContentType.PHOTO, 
            ContentType.TEXT, 
            ContentType.STICKER, 
            ContentType.AUDIO,
            ContentType.DOCUMENT
        }))
async def say_any(message: Message):
    await message.answer(
        text='Нет такого варианта ответа',
        reply_markup= kb.to_main
    )