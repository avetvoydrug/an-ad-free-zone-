import asyncio
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.exceptions import TelegramRetryAfter
from typing import Callable, Dict, Any, Awaitable

from menu.database.requests import check_status

class AntiSpamMiddleware(BaseMiddleware):
    """
    Простой middleware для защиты от спама в aiogram 3.8

    Атрибуты:
        limit (int): Максимальное количество сообщений от пользователя за время cooldown
        cooldown (int): Время (в секундах) для сброса счетчика сообщений пользователя

    Методы:
        on_process_message(self, message: Message, data: dict): Обработчик сообщений
    """

    def __init__(self, limit: int = 3, cooldown: int = 5):
        """
        Инициализация класса AntiSpamMiddleware

        Args:
            limit (int): Максимальное количество сообщений от пользователя за время cooldown
            cooldown (int): Время (в секундах) для сброса счетчика сообщений пользователя
        """
        super().__init__()
        self.limit = limit
        self.cooldown = cooldown
        self.cache = {}  # Словарь для хранения времени последнего сообщения пользователя

    async def on_process_message(self,
                       message: Message,
                       data: dict):
        """
        Обработчик сообщений

        Args:
            message (Message): Объект сообщения Telegram
            data (dict): Данные, передаваемые между middleware

        Returns:
            None: Если сообщение не является спамом
            None: Если спам, сообщение не передается дальше по цепочке обработки
        """
        
        user_id = message.from_user.id
        flag = await check_status(user_id)
        if not flag:
            # Проверка, отправлял ли пользователь сообщения ранее
            if user_id in self.cache:
                last_message_time = self.cache[user_id]
                time_passed = message.date.timestamp() - last_message_time

                # Проверка на превышение лимита сообщений
                if time_passed < self.cooldown:
                    # Отправка сообщения об ожидании
                    try:
                        # Удаляем сообщение, если оно помечено как спам
                        await message.delete()
                        await message.answer(f"Пожалуйста, подождите {self.cooldown} секунд перед отправкой следующего сообщения.")
                    except TelegramRetryAfter as e:
                        # Обработка ошибки, если сообщение отправлено слишком быстро
                        await asyncio.sleep(e.timeout)
                        await message.edit_text(f"Подождите {self.cooldown} секунд перед отправкой следующего сообщения.")
                    return True
            # Обновление времени последнего сообщения пользователя
            self.cache[user_id] = message.date.timestamp()
        else: return
    
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        flag = await self.on_process_message(event, data)
        if not flag:
            return await handler(event, data)

    