from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def dict(self: Self) -> dict:
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


sqlite_file_name = "database.db"
sqlite_url = f"sqlite+aiosqlite:///{sqlite_file_name}"

engine = create_async_engine(sqlite_url, echo=True)


class _DbConnector:
    def __init__(self: Self, engine: AsyncEngine) -> None:
        self.engine = engine
        self.session_factory = async_sessionmaker(
            engine, expire_on_commit=False
        )
        return None

    @asynccontextmanager
    async def connect(self: Self) -> AsyncGenerator[AsyncSession]:
        async with self.session_factory() as session:
            yield session
