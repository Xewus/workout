"""HTML-страницы, связанные с тренировками."""

from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer
import datetime as dt

from src.core.enums.pages import WorkoutPages
from src.core.typings import ApiRequest

from .._deps import DbDep, UserCookieDep

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

plans_router = APIRouter()


@plans_router.get("")
async def plans(request: ApiRequest, db: DbDep, user: UserCookieDep, only_mine: bool = False, offset: int = 0, limit: int = 10):
    """Страница с планами тренировок."""
    user_id = user.id if only_mine else None
    plans = await db.workout.get_plans(offset=offset, limit=limit, user_id=user_id)
    data = {"request": request, "user": user, "plans": plans}
    return request.app.templates.TemplateResponse(WorkoutPages.PLANS.value, data)   

@plans_router.get("/create")
def create_plan(request: ApiRequest, user: UserCookieDep):
    """Страница создания нового плана тренировок."""
    data = {"request": request}
    return request.app.templates.TemplateResponse(WorkoutPages.CREATE_PLAN.value, data)


@plans_router.get("/{plan_id}")
async def get_full_plan(request: ApiRequest, db: DbDep, _: UserCookieDep, plan_id: int):
    """Получить тренировочный план по идентификатору."""
    plan = await db.workout.get_full_plan_by_id(plan_id)
    if not plan:
        raise HTTPException(status_code=404)

    data ={
        "request": request,
        "plan": plan,
        "today_date": dt.date.today().isoformat(),
    }
    return request.app.templates.TemplateResponse(WorkoutPages.PLAN.value, data) 


@plans_router.get("/{plan_id}/{date}")
async def get_workout_day(request: ApiRequest, db: DbDep, plan_id: int, date: dt.date):
    # Здесь мы получаем данные из БД (как делали в сервисах)
    day = await db.workout.get_day(plan_id, date)
    if not day:
        return {"error": "Plan not found"}

    return request.app.templates.TemplateResponse(
        WorkoutPages.DAY.value, {"request": request, "day": day})
