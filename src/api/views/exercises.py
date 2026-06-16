"""HTML-страницы, связанные с упражнениями."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer

from src.core.enums.pages import WorkoutPages
from src.core.typings import ApiRequest

from .._deps import DbDep, UserCookieDep

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

exercises_router = APIRouter()

@exercises_router.get("")
async def exercises(request: ApiRequest,  db: DbDep, user: UserCookieDep, offset: int = 0, limit: int = 10) -> HTMLResponse:
    """Отдать страницу со списком упражнений.

    Args:
        request (ApiRequest): Текущий запрос.
        db (Db): Контейнер репозиториев.
        user (UserModel): Текущий пользователь из cookie-токена.
        offset (int): Смещение выборки.
        limit (int): Максимальное число упражнений.

    Returns:
        HTMLResponse: Отрендеренная страница со списком упражнений.
    """
    exercises = await db.workout.get_exercises(offset=offset, limit=limit)
    data = {"request": request, "user": user, "exercises": exercises}
    return request.app.templates.TemplateResponse(WorkoutPages.EXERCISES.value, data)  


@exercises_router.get("/create")
def create_exercises(request: ApiRequest, user: UserCookieDep) -> HTMLResponse:
    """Отдать страницу добавления упражнения.

    Args:
        request (ApiRequest): Текущий запрос.
        user (UserModel): Текущий пользователь из cookie-токена.

    Returns:
        HTMLResponse: Отрендеренная страница создания упражнения.
    """
    data = {"request": request}
    return request.app.templates.TemplateResponse(WorkoutPages.CREATE_EXERCISE.value, data)


@exercises_router.get("/{exercise_id}")
async def get_exercises(request: ApiRequest, db: DbDep, _: UserCookieDep, exercise_id: int) -> HTMLResponse:
    """Отдать страницу упражнения по идентификатору.

    Args:
        request (ApiRequest): Текущий запрос.
        db (Db): Контейнер репозиториев.
        _ (UserModel): Текущий пользователь (требуется авторизация).
        exercise_id (int): Идентификатор упражнения.

    Returns:
        HTMLResponse: Отрендеренная страница упражнения.

    Raises:
        HTTPException: 404, если упражнение не найдено.
    """
    exercise = await db.workout.get_exercise_by_id(exercise_id)
    if not exercise:
        raise HTTPException(status_code=404)

    data ={"request": request, "exercise": exercise}
    return request.app.templates.TemplateResponse(WorkoutPages.EXERCISE.value, data) 

