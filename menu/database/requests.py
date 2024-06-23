from menu.database.models import async_session
from menu.database.models import Subscription, Film, Serie
from sqlalchemy import select

async def get_subscription():
    async with async_session() as session:
        return await session.scalars(select(Subscription))

async def get_series(code):
    try:
        async with async_session() as session:
            series = await session.scalars(select(Serie).where(Serie.films_id == code))
            if series: return series
            else:
                return False
    except Exception:
        print('get_series')

async def get_film(code):
    async with async_session() as session:
        film = await session.scalar(select(Film).where(Film.films_id == code))
        if film: return film
        else:
            return False