import os
from dotenv import load_dotenv
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ContentType, CallbackQuery

from aiogram.fsm.context import FSMContext
from menu.states import Search, Call_us

import menu.keyboards as kb
from menu.tg_api import is_sub
from menu.database.requests import get_film, get_series
from menu.middlewares import AntiSpamMiddleware

router = Router()
load_dotenv()
router.message.middleware(AntiSpamMiddleware(limit=4, cooldown=5))


@router.message(CommandStart())
async def cmd_start(message: Message):
    #await rq.set_user(message.from_user.id) идент tg_id в бд
    #припилить видос с гайдом к приветственному месседжу
    await message.answer('Приветствуем Вас в зоне без рекламы ;)', reply_markup=kb.main)

####################ANY_HANDLERS#####################        


@router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery):
    await callback.message.edit_text('Приветствуем Вас в зоне без рекламы ;)', reply_markup=kb.main)

@router.callback_query(F.data == 'to_main_wo_edit')
async def to_main(callback: CallbackQuery):
    await callback.message.answer('Приветствуем Вас в зоне без рекламы ;)', reply_markup=kb.main)

@router.message(F.text.startswith('кинь'))
async def video_file_id(message: Message):
    await message.answer_video(video='BAACAgIAAxkBAAMFZnGkOIqtILTirBkC4DfANzRumyAAAsFQAAOqkEtfGbJo6xg7sDUE')
    #await message.answer(message.video.file_id)

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
                    await state.set_state(Search.code)
                    await message.answer('Такого кода не существует\nВведите корректно ;)')
            else:
                await state.set_state(Search.code)
                await message.answer('Такого кода не существует\nВведите корректно ;)')
        except Exception:
            await state.set_state(Search.code)
            await message.answer(f'{message.from_user.first_name}, код должен состоять только из цифр\nВы ввели: {data["code"]}\nПовторите ввод корректно :)')
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