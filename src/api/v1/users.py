from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated

from src.db import UserModel
from src.dto import UserDTO, TokenDTO

from .._deps import DbDep, UserJWTDep
from .._security import hash_password, authenticate_user, create_jwt

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/signup")
def signup(data: Annotated[UserDTO, Form()], db: DbDep):
    """Регистрация нового пользователя."""
    hashed_pass=hash_password(data.password)
    user = UserModel(hashed_password = hashed_pass, **data.model_dump(exclude={"password"}))
    if err := db.user.create(user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    return {"message": f"Пользователь {user.username} успешно зарегистрирован!"}
    

@router.post("/token")
async def get_access_token(
    db: DbDep,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenDTO:
    """Получение JWT-токена по имени пользователя и паролю."""
    if not (user := authenticate_user(db, form.username, form.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь с таким именем и паролем не найден.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenDTO(access_token=create_jwt(user))


@router.get("/me", response_model=UserDTO, response_model_exclude={"hashed_password"})
async def read_users_me(user: UserJWTDep):
    """Получение информации о текущем пользователе."""
    return user