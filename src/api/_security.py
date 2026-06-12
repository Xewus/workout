from __future__ import annotations

import datetime as dt
from typing import Annotated

from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from src.db import Db, get_db, UserModel

from src.config import config

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=config.TOKEN_URL)


def hash_password(password: bytes | str) -> str:
    return password_hash.hash(password)

    
def authenticate_user(db: Db, username: str, password: str) -> UserModel | None:
    """Проверка наличия пользователя с данным именем и паролем в БД."""
    if not (user := db.user.get_by_username(username)):
        return None

    if not password_hash.verify(password, user.hashed_password):
        return None

    return user

def create_jwt(user: UserModel) -> str:
    """Создание JWT-токена для данного пользователя."""
    expire = dt.datetime.now(dt.UTC) + dt.timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode ={"sub": user.username, "exp": expire}

    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

def _get_user_by_token(db: Db, token: str) -> UserModel:
    """Получение пользователя по JWT-токену."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный логин или пароль.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = db.user.get_by_username(username)
    if user is None:
        raise credentials_exception

    return user

def get_cookie_user(db: Annotated[Db, Depends(get_db)], access_token: Annotated[str | None, Cookie()] = None) -> UserModel:
    """Определение пользователя по JWT-токену из cookie."""
    if not access_token:
        raise HTTPException(status_code=401, detail="Токен не найден в cookie.")
    return _get_user_by_token(db, access_token)

def get_jwt_user(db: Annotated[Db, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]) -> UserModel:
    """Определение пользователя по JWT-токену"""
    return _get_user_by_token(db, token)
