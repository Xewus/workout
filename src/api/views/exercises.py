"""HTML-страницы, связанные с упражнениями."""

from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer

from src.core.enums.pages import WorkoutPages
from src.core.typings import ApiRequest

from .._deps import DbDep, UserCookieDep

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

exercises_router = APIRouter()

@exercises_router.get("")
async def exercises(request: ApiRequest,  db: DbDep, user: UserCookieDep, offset: int = 0, limit: int = 10):
    exercises = db.workout.get_exercises(offset=offset, limit=limit)
    data = {"request": request, "user": user, "exercises": exercises}
    return request.app.templates.TemplateResponse(WorkoutPages.EXERCISES.value, data)  


@exercises_router.get("/create")
def create_exercises(request: ApiRequest, user: UserCookieDep):
    """Страница создания добавления упражнения."""
    data = {"request": request}
    return request.app.templates.TemplateResponse(WorkoutPages.CREATE_EXERCISE.value, data)


@exercises_router.get("/{exercise_id}")
async def get_exercises(request: ApiRequest, db: DbDep, _: UserCookieDep, exercise_id: int):
    """Получить тренировочный план по идентификатору."""
    exercise = db.workout.get_exercise_by_id(exercise_id)
    if not exercise:
        raise HTTPException(status_code=404)

    data ={"request": request, "exercise": exercise}
    return request.app.templates.TemplateResponse(WorkoutPages.EXERCISE.value, data) 

