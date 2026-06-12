from typing import Annotated

from fastapi import Depends

from src.db import get_db, Db, UserModel

from ._security import get_jwt_user, get_cookie_user

DbDep = Annotated[Db, Depends(get_db)]
UserCookieDep = Annotated[UserModel, Depends(get_cookie_user)]
UserJWTDep = Annotated[UserModel, Depends(get_jwt_user)]
