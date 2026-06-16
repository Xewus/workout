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
    """Вычислить хэш пароля.

    Args:
        password (bytes | str): Пароль в открытом виде.

    Returns:
        str: Хэш пароля для хранения в БД.
    """
    return password_hash.hash(password)

    
async def authenticate_user(db: Db, username: str, password: str) -> UserModel | None:
    """Проверить имя и пароль пользователя.

    Args:
        db (Db): Контейнер репозиториев.
        username (str): Имя пользователя.
        password (str): Пароль в открытом виде.

    Returns:
        UserModel | None: Пользователь при успешной проверке, иначе ``None``.
    """
    if not (user := await db.user.get_by_username(username)):
        return None

    if not password_hash.verify(password, user.hashed_password):
        return None

    return user

def create_jwt(user: UserModel) -> str:
    """Создать JWT-токен для пользователя.

    Args:
        user (UserModel): Пользователь, для которого выпускается токен.

    Returns:
        str: Подписанный JWT-токен доступа.
    """
    expire = dt.datetime.now(dt.UTC) + dt.timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode ={"sub": user.username, "exp": expire}

    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

async def _get_user_by_token(db: Db, token: str) -> UserModel:
    """Декодировать токен и найти соответствующего пользователя.

    Args:
        db (Db): Контейнер репозиториев.
        token (str): JWT-токен доступа.

    Returns:
        UserModel: Пользователь, закодированный в токене.

    Raises:
        HTTPException: 401, если токен невалиден или пользователь не найден.
    """
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

    user = await db.user.get_by_username(username)
    if user is None:
        raise credentials_exception

    return user

async def get_cookie_user(db: Annotated[Db, Depends(get_db)], access_token: Annotated[str | None, Cookie()] = None) -> UserModel:
    """Определить текущего пользователя по токену из cookie (зависимость FastAPI).

    Args:
        db (Db): Контейнер репозиториев.
        access_token (str | None): Токен доступа из cookie.

    Returns:
        UserModel: Текущий пользователь.

    Raises:
        HTTPException: 401, если cookie с токеном отсутствует.
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Токен не найден в cookie.")
    return await _get_user_by_token(db, access_token)

async def get_jwt_user(db: Annotated[Db, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]) -> UserModel:
    """Определить текущего пользователя по Bearer-токену (зависимость FastAPI).

    Args:
        db (Db): Контейнер репозиториев.
        token (str): JWT-токен из заголовка Authorization.

    Returns:
        UserModel: Текущий пользователь.
    """
    return await _get_user_by_token(db, token)
