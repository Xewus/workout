"""Переиспользуемые зависимости FastAPI для внедрения в эндпоинты."""
from typing import Annotated

from fastapi import Depends

from src.db import get_db, Db, UserModel

from ._security import get_jwt_user, get_cookie_user

# Контейнер CRUD-репозиториев.
DbDep = Annotated[Db, Depends(get_db)]
# Текущий пользователь, определённый по токену из cookie.
UserCookieDep = Annotated[UserModel, Depends(get_cookie_user)]
# Текущий пользователь, определённый по Bearer-токену.
UserJWTDep = Annotated[UserModel, Depends(get_jwt_user)]
