"""HTML-страницы, связанные с пользователями."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
import datetime as dt

from src.core.enums.pages import UserPages
from src.core.typings import ApiRequest

from .._deps import UserCookieDep

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



@router.get("/signup")
def signup(request: ApiRequest) -> HTMLResponse:
    """Отдать страницу регистрации нового пользователя.

    Args:
        request (ApiRequest): Текущий запрос.

    Returns:
        HTMLResponse: Отрендеренная страница регистрации.
    """
    return request.app.templates.TemplateResponse(UserPages.SIGNUP.value, {"request": request})

@router.get("/login")
def login(request: ApiRequest) -> HTMLResponse:
    """Отдать страницу входа.

    Args:
        request (ApiRequest): Текущий запрос.

    Returns:
        HTMLResponse: Отрендеренная страница входа.
    """
    return request.app.templates.TemplateResponse(UserPages.LOGIN.value, {"request": request})

@router.get("/me")
def profile(request: ApiRequest, user: UserCookieDep) -> HTMLResponse:
    """Отдать страницу профиля текущего пользователя.

    Args:
        request (ApiRequest): Текущий запрос.
        user (UserModel): Текущий пользователь из cookie-токена.

    Returns:
        HTMLResponse: Отрендеренная страница профиля с возрастом пользователя.
    """
    age = (dt.date.today() - user.birth_date).days // 365.25
    return request.app.templates.TemplateResponse(UserPages.PROFILE.value, {"request": request, "user": user, "age": age})
