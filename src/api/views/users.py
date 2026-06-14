"""HTML-страницы, связанные с пользователями."""
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer
import datetime as dt

from src.core.enums.pages import UserPages
from src.core.typings import ApiRequest

from .._deps import UserCookieDep

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



@router.get("/signup")
def signup(request: ApiRequest):
    """Страница регистрации нового пользователя."""
    return request.app.templates.TemplateResponse(UserPages.SIGNUP.value, {"request": request})

@router.get("/login")
def login(request: ApiRequest):
    """Страница входа."""
    print(ApiRequest.headers)
    return request.app.templates.TemplateResponse(UserPages.LOGIN.value, {"request": request})

@router.get("/me")
def profile(request: ApiRequest, user: UserCookieDep):
    """Страница профиля текущего пользователя."""
    age = (dt.date.today() - user.birth_date).days // 365.25
    return request.app.templates.TemplateResponse(UserPages.PROFILE.value, {"request": request, "user": user, "age": age})
