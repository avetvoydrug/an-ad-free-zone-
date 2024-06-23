import os
import requests
from menu.database.requests import get_subscription
from dotenv import load_dotenv

load_dotenv()

class SubscriptionChecker:

    def __init__(self, bot_token: str):
        self.bot_token = bot_token

    def check_subscription(self, channel_id: str, user_id: int) -> bool:
        """Проверяет подписку пользователя на канал с помощью API Telegram.

        Args:
            channel_id (str): ID канала в формате '@channel_name'.
            user_id (int): ID пользователя Telegram.

        Returns:
            bool: True, если пользователь подписан на канал, иначе False.
        """
        url = f"https://api.telegram.org/bot{self.bot_token}/getChatMember?chat_id={channel_id}&user_id={user_id}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['result']['status'] in ("administrator", "creator", "member")
        else:
            return False

async def is_sub(tg_id: int):
    checker = SubscriptionChecker(os.getenv('TOKEN'))
    all_subs = await get_subscription()
    count = 0
    count_subs = 0
    for sub in all_subs:
        count_subs += 1
        is_subscribed = checker.check_subscription(sub.dog_link, tg_id)
        if is_subscribed:
            count += 1
    if count == count_subs:
        return True
    else:
        return False
