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
    """Базовый класс для всех ORM-моделей приложения."""

    def dict(self: Self) -> dict[str, object]:
        """Сериализовать модель в словарь по её колонкам.

        Returns:
            dict[str, object]: Отображение "имя колонки -> значение".
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


sqlite_file_name = "database.db"
sqlite_url = f"sqlite+aiosqlite:///{sqlite_file_name}"

engine = create_async_engine(sqlite_url, echo=True)


class _DbConnector:
    """Базовый класс CRUD, владеющий асинхронной фабрикой сессий."""

    def __init__(self: Self, engine: AsyncEngine) -> None:
        """Создать коннектор поверх асинхронного движка.

        Args:
            engine (AsyncEngine): Асинхронный движок SQLAlchemy.
        """
        self.engine = engine
        self.session_factory = async_sessionmaker(
            engine, expire_on_commit=False
        )
        return None

    @asynccontextmanager
    async def connect(self: Self) -> AsyncGenerator[AsyncSession]:
        """Открыть асинхронную сессию БД в виде контекстного менеджера.

        Yields:
            AsyncSession: Активная асинхронная сессия SQLAlchemy.
        """
        async with self.session_factory() as session:
            yield session
