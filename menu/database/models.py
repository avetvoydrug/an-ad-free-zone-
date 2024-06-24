from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

import os
from dotenv import load_dotenv

load_dotenv()
engine = create_async_engine(url=os.getenv('SQLALCHEMY_URL'))

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id = mapped_column(BigInteger)
    status: Mapped[int] = mapped_column(default=0)

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dog_link: Mapped[str] = mapped_column(String(33))
    url: Mapped[str] = mapped_column(String(50))

class Film(Base):
    __tablename__ = 'films'

    films_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    #tg_file_id: Mapped[str] = mapped_column(String(80))

class Serie(Base):
    __tablename__ = 'series'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    films_id: Mapped[int] = mapped_column(ForeignKey('films.films_id', ondelete='CASCADE'))
    season: Mapped[int] = mapped_column()
    part: Mapped[int] = mapped_column()
    tg_file_id: Mapped[str] = mapped_column(String(80))

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        