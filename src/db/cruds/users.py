from __future__ import annotations

from typing import Self

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .._base import _DbConnector
from ..models.users import UserModel


class UserCRUD(_DbConnector):
    """Асинхронные операции с пользователями в БД."""

    async def create(self: Self, user: UserModel) -> str | None:
        """Сохранить нового пользователя.

        Args:
            user (UserModel): Пользователь для добавления в БД.

        Returns:
            str | None: Текст ошибки при конфликте уникальности,
                иначе ``None`` при успешном создании.
        """
        async with self.connect() as db:
            db.add(user)
            try:
                await db.commit()
            except IntegrityError:
                await db.rollback()
                return f"Пользователь с именем {user.username} уже существует."

            await db.refresh(user)
            return None

    async def get_by_pass(self: Self, password: str) -> UserModel | None:
        """Найти пользователя по хэшу пароля.

        Args:
            password (str): Хэш пароля для поиска.

        Returns:
            UserModel | None: Найденный пользователь либо ``None``.
        """
        async with self.connect() as db:
            result = await db.execute(select(UserModel).where(UserModel.hashed_password == password).limit(1))
            return result.scalar_one_or_none()

    async def get_by_username(self: Self, username: str) -> UserModel | None:
        """Найти пользователя по имени.

        Args:
            username (str): Имя пользователя для поиска.

        Returns:
            UserModel | None: Найденный пользователь либо ``None``.
        """
        async with self.connect() as db:
            result = await db.execute(select(UserModel).where(UserModel.username == username).limit(1))
            return result.scalar_one_or_none()
