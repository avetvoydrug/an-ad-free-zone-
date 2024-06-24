from menu.database.models import async_session
from menu.database.models import Subscription, Film, Serie, User
from sqlalchemy import select, update, func, delete

####################SUB_REQUEST#####################

async def get_subscription():
    async with async_session() as session:
        return await session.scalars(select(Subscription))


####################Films/Series_requests#####################

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
        
async def set_film(code: int, name: str):
    async with async_session() as session:
        session.add(Film(films_id=code, name=name))
        await session.commit()

async def set_serie(code: int, season: int, part: int, tg_file_id: str):
    async with async_session() as session:
        session.add(Serie(films_id=code, season=season, part=part, tg_file_id=tg_file_id))
        await session.commit()

async def get_last_film_code():
    async with async_session() as session:
        film = await session.scalar(select(func.max(Film.films_id)))
        return film

async def get_some_serie(films_id: int, season: int, part: int):
    async with async_session() as session:
        serie = await session.execute(
            select(Serie.id).where(
                Serie.films_id == films_id,
                Serie.season == season,
                Serie.part == part
            ))
        if serie is not None: return serie
        else: return 0 

async def update_film(code: int, name: str):
    async with async_session() as session:
        await session.execute(update(Film).where(Film.films_id == code).values(name=f'{name}'))
        await session.commit()

async def delete_serie(code: int):
    async with async_session() as sesion:
        await sesion.execute(delete(Serie).where(Serie.id == code))
        await sesion.commit()

async def delete_film(code: int):
    async with async_session() as session:
        await session.execute(delete(Film).where(Film.films_id == code))
        await session.commit()
        
####################USERS_REQUESTS#####################

async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def check_status(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user.status == 1: return True
        else: False

async def set_admin(tg_id: int) -> None:
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id).values(status=1))
        await session.commit()

async def get_users():
    async with async_session() as session:
        return await session.scalars(select(User))