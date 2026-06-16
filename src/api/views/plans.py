"""HTML-страницы, связанные с тренировками."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
import datetime as dt

from src.core.enums.pages import WorkoutPages
from src.core.typings import ApiRequest

from .._deps import DbDep, UserCookieDep

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

plans_router = APIRouter()


@plans_router.get("")
async def plans(request: ApiRequest, db: DbDep, user: UserCookieDep, only_mine: bool = False, offset: int = 0, limit: int = 10) -> HTMLResponse:
    """Отдать страницу со списком планов тренировок.

    Args:
        request (ApiRequest): Текущий запрос.
        db (Db): Контейнер репозиториев.
        user (UserModel): Текущий пользователь из cookie-токена.
        only_mine (bool): Если ``True``, показываются только планы пользователя.
        offset (int): Смещение выборки.
        limit (int): Максимальное число планов.

    Returns:
        HTMLResponse: Отрендеренная страница со списком планов.
    """
    user_id = user.id if only_mine else None
    plans = await db.workout.get_plans(offset=offset, limit=limit, user_id=user_id)
    data = {"request": request, "user": user, "plans": plans}
    return request.app.templates.TemplateResponse(WorkoutPages.PLANS.value, data)   

@plans_router.get("/create")
def create_plan(request: ApiRequest, user: UserCookieDep) -> HTMLResponse:
    """Отдать страницу создания нового плана тренировок.

    Args:
        request (ApiRequest): Текущий запрос.
        user (UserModel): Текущий пользователь из cookie-токена.

    Returns:
        HTMLResponse: Отрендеренная страница создания плана.
    """
    data = {"request": request}
    return request.app.templates.TemplateResponse(WorkoutPages.CREATE_PLAN.value, data)


@plans_router.get("/{plan_id}")
async def get_full_plan(request: ApiRequest, db: DbDep, _: UserCookieDep, plan_id: int) -> HTMLResponse:
    """Отдать страницу полного тренировочного плана по идентификатору.

    Args:
        request (ApiRequest): Текущий запрос.
        db (Db): Контейнер репозиториев.
        _ (UserModel): Текущий пользователь (требуется авторизация).
        plan_id (int): Идентификатор тренировочного плана.

    Returns:
        HTMLResponse: Отрендеренная страница плана с днями и упражнениями.

    Raises:
        HTTPException: 404, если план не найден.
    """
    plan = await db.workout.get_full_plan_by_id(plan_id)
    if not plan:
        raise HTTPException(status_code=404)

    data ={
        "request": request,
        "plan": plan,
        "today_date": dt.date.today().isoformat(),
    }
    return request.app.templates.TemplateResponse(WorkoutPages.PLAN.value, data) 


@plans_router.get("/{plan_id}/{date}", response_model=None)
async def get_workout_day(request: ApiRequest, db: DbDep, plan_id: int, date: dt.date) -> HTMLResponse | dict[str, str]:
    """Отдать страницу дня тренировки по плану и дате.

    Args:
        request (ApiRequest): Текущий запрос.
        db (Db): Контейнер репозиториев.
        plan_id (int): Идентификатор тренировочного плана.
        date (dt.date): Дата дня тренировки.

    Returns:
        HTMLResponse | dict[str, str]: Отрендеренная страница дня тренировки
            либо словарь с ошибкой, если день не найден.
    """
    # Получаем агрегированные данные дня (день + упражнения) одним запросом.
    day = await db.workout.get_day(plan_id, date)
    if not day:
        return {"error": "Plan not found"}

    return request.app.templates.TemplateResponse(
        WorkoutPages.DAY.value, {"request": request, "day": day})
