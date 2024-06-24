from aiogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,
                           KeyboardButton, InlineKeyboardButton,
                           KeyboardButtonRequestUser)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from menu.database.requests import get_subscription, get_film, get_series

main = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Найти фильм', callback_data='find_films')],
                                     [InlineKeyboardButton(text='По рекламе', callback_data='ads')]],
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
            text='Отправить ссылку на аккаунт',
            request_user=KeyboardButtonRequestUser(
                request_id=True
            ))]],
        resize_keyboard=True,
        input_field_placeholder='Нажмите, что отправить')

approve = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Отправить', callback_data='approve')],
        [InlineKeyboardButton(text='Изменить', callback_data='change')]
    ],
)

####################SUB_KEYBOARDS#####################

async def subscriptions():
    all_subs = await get_subscription()
    keyboard = InlineKeyboardBuilder()
    for sub in all_subs:
        keyboard.add(InlineKeyboardButton(text=f'{sub.id}', url=sub.url, callback_data=f'sub_{sub.id}'))
    keyboard.add(InlineKeyboardButton(text='Я подписался!', callback_data='find_films'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()

####################Drop_Series_KEYBOARDS#####################

async def series(code: int):
    all_series = await get_series(code)
    film = await get_film(code)
    keyboard = InlineKeyboardBuilder()
    for serie in all_series.all():
        keyboard.add(InlineKeyboardButton(
            text=f'{film.name[:2]}Se{serie.season}P{serie.part}',
            callback_data=f'season_{code}_{serie.season}_{serie.part}'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main_wo_edit'))
    return keyboard.adjust(2).as_markup()

####################to_main_KEYBOARDS#####################

to_main = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='На главную', callback_data='to_main')]])
#на главную в некст клавах
                     