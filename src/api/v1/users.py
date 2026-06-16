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
async def signup(data: Annotated[UserDTO, Form()], db: DbDep) -> dict[str, str]:
    """Зарегистрировать нового пользователя.

    Args:
        data (UserDTO): Данные регистрации из формы.
        db (Db): Контейнер репозиториев.

    Returns:
        dict[str, str]: Сообщение об успешной регистрации.

    Raises:
        HTTPException: 400, если пользователь с таким именем уже существует.
    """
    hashed_pass=hash_password(data.password)
    user = UserModel(hashed_password = hashed_pass, **data.model_dump(exclude={"password"}))
    if err := await db.user.create(user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    return {"message": f"Пользователь {user.username} успешно зарегистрирован!"}
    

@router.post("/token")
async def get_access_token(
    db: DbDep,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenDTO:
    """Выдать JWT-токен по имени пользователя и паролю.

    Args:
        db (Db): Контейнер репозиториев.
        form (OAuth2PasswordRequestForm): Форма с именем и паролем.

    Returns:
        TokenDTO: Токен доступа.

    Raises:
        HTTPException: 401, если учётные данные неверны.
    """
    if not (user := await authenticate_user(db, form.username, form.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь с таким именем и паролем не найден.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenDTO(access_token=create_jwt(user))


@router.get("/me", response_model=UserDTO, response_model_exclude={"hashed_password"})
async def read_users_me(user: UserJWTDep) -> UserModel:
    """Вернуть информацию о текущем пользователе.

    Args:
        user (UserModel): Текущий пользователь из Bearer-токена.

    Returns:
        UserModel: Текущий пользователь (сериализуется как ``UserDTO``).
    """
    return user