from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlalchemy import (SQLAlchemyBaseUserTable,
                                         SQLAlchemyUserDatabase)
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker

Base: DeclarativeMeta = declarative_base()

DATABASE_NAME = "applications.sqlite"

engine = create_async_engine(f"sqlite+aiosqlite:///{DATABASE_NAME}")
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class UserTable(Base, SQLAlchemyBaseUserTable):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    hashed_password: str = Column(String(length=1024), nullable=False)
    avatar = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, UserTable)
