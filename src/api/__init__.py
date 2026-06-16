"""Корневой роутер приложения: главная страница и подключение API/страниц."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from src.core.typings import ApiRequest

from .v1 import router as v1_router
from .views import router as views_router

api_router = APIRouter(prefix="/api")
api_router.include_router(v1_router)
api_router.include_router(views_router, include_in_schema=False)

main_router = APIRouter()

@main_router.get("/", include_in_schema=False)
def index(request: ApiRequest) -> HTMLResponse:
    """Отдать главную страницу приложения.

    Args:
        request (ApiRequest): Текущий запрос.

    Returns:
        HTMLResponse: Отрендеренная главная страница.
    """
    return request.app.templates.TemplateResponse("index.html", {"request": request})

@main_router.get(".well-known/appspecific/com.chrome.devtools.json", include_in_schema=False)
def devtools() -> dict[str, str]:
    """Заглушка для запроса Chrome DevTools.

    Returns:
        dict[str, str]: Пустой объект.
    """
    return {}

main_router.include_router(api_router)
