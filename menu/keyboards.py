from aiogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,
                           KeyboardButton, InlineKeyboardButton,
                           KeyboardButtonRequestUser)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from menu.database.requests import get_subscription, get_film, get_series, get_seasons

main = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Найти фильм🍕', callback_data='find_films')],
                                     [InlineKeyboardButton(text='По сотрудничеству💻', callback_data='ads')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')


####################ADMIN_KEYBOARDS#####################


admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Добавить существующий', callback_data='add_admin'),
         InlineKeyboardButton(text='Добавить новый', callback_data='add_new_admin'),
         InlineKeyboardButton(text='Получить код серии', callback_data='get_code_serie_admin')],
        [InlineKeyboardButton(text='Удалить серию', callback_data='delete_admin'),
         InlineKeyboardButton(text='Удалить полностью', callback_data='delete_full_admin'),
         InlineKeyboardButton(text='Исправить ленту', callback_data='change_film_admin')],
        [InlineKeyboardButton(text='Узнать file_ID', callback_data='file_id_admin'),
         InlineKeyboardButton(text='Получить последний код', callback_data='get_code_admin'),
         InlineKeyboardButton(text='Отправить рассылку', callback_data='send_admin')],
        [InlineKeyboardButton(text='Выдать админку', callback_data='set_admin')]
    ]
)


####################ADS_KEYBOARDS#####################

send_link = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(
            text='Отправить ссылку на аккаунт🦄',
            request_user=KeyboardButtonRequestUser(
                request_id=True
            ))]],
        resize_keyboard=True,
        input_field_placeholder='Нажмите, чтобы отправить')

approve = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Отправить✈️', callback_data='approve')],
        [InlineKeyboardButton(text='Изменить✍️', callback_data='change')]
    ],
)

####################SUB_KEYBOARDS#####################

async def subscriptions():
    all_subs = await get_subscription()
    keyboard = InlineKeyboardBuilder()
    for sub in all_subs:
        keyboard.add(InlineKeyboardButton(text=f'{sub.id}', url=sub.url, callback_data=f'sub_{sub.id}'))
    keyboard.add(InlineKeyboardButton(text='Я подписался!🎉', callback_data='find_films'))
    keyboard.add(InlineKeyboardButton(text='На главную🏝️', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()

####################Drop_Series_KEYBOARDS#####################

async def series(code: int, season=1):
    all_series = await get_series(code, season)
    film = await get_film(code)
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Выбрать сезон✈️', callback_data=f'choose_season_{code}'))
    for serie in all_series.all():
        keyboard.add(InlineKeyboardButton(
            text=f'{film.name[:4]} Сезон{serie.season} серия{serie.part} 🎞',
            callback_data=f'season_{code}_{serie.season}_{serie.part}'))
    keyboard.add(InlineKeyboardButton(text='На главную🏝️', callback_data='to_main_wo_edit'))
    return keyboard.adjust(2).as_markup()

async def seasons(code: int):
    seasons = await get_seasons(code)
    keyboard = ReplyKeyboardBuilder()
    for season in seasons:
        keyboard.add(KeyboardButton(text=f'{season[0]}'))
    return keyboard.adjust(3).as_markup()

####################to_main_KEYBOARDS#####################

to_main = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='На главную🏝️', callback_data='to_main')]])
#на главную в некст клавах
                     