from __future__ import annotations

from typing import Self

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .._base import _DbConnector
from ..models.users import UserModel


class UserCRUD(_DbConnector):
    def create(self: Self, user: UserModel) -> str | None:
        with self.connect() as db:
            db.add(user)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                return f"Пользователь с именем {user.username} уже существует."

            return db.refresh(user)

    def get_by_pass(self: Self, password: str) -> UserModel | None:
        with self.connect() as db:
            result = db.execute(select(UserModel).where(UserModel.hashed_password == password).limit(1))
            return result.scalar_one_or_none()
    
    def get_by_username(self: Self, username: str) -> UserModel | None:
        with self.connect() as db:
            result = db.execute(select(UserModel).where(UserModel.username == username).limit(1))
            return result.scalar_one_or_none()
