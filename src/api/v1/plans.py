import datetime as dt
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Form, HTTPException, Query, UploadFile, status, Depends
from fastapi.params import File

from src.core.typings import ApiRequest
from src.db import ExerciseModel,  WorkoutDayModel, WorkoutPlanModel, UserModel, ExerciseInDayModel
from src.dto import CreatePlanDTO,CreateDayDTO, AddExerciseDTO

from .._deps import DbDep, UserCookieDep

from .._security import get_cookie_user

plans_router = APIRouter()


@plans_router.post("/create")
async def create_plan(db: DbDep, user: UserCookieDep, data: CreatePlanDTO) -> int:
    """Создать новый тренировочный план для текущего пользователя.

    Args:
        db (Db): Контейнер репозиториев.
        user (UserModel): Текущий пользователь-владелец плана.
        data (CreatePlanDTO): Данные создаваемого плана.

    Returns:
        int: Идентификатор созданного плана.

    Raises:
        HTTPException: 400, если план не удалось создать.
    """
    model = WorkoutPlanModel(title=data.title, description=data.description or "", user_id=user.id)
    if err := await db.workout.create_plan(model):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    return model.id

# @plans_router.get("/plans")
# async def list_plans(*, db: DbDep, user: Annotated[UserModel, Depends(get_cookie_user)], only_mine: bool = False, offset: int = 0, limit: int = 10):
#     """Получить список тренировочных планов."""
#     user_id = user.id if only_mine else None
#     plans = db.workout.get_plans(offset=offset, limit=limit, user_id=user_id)
#     return plans


@plans_router.post("/workout_day")
async def create_workout_day(db: DbDep, user: UserCookieDep, data: CreateDayDTO) -> str | None:
    """Создать новый день тренировки для конкретного плана.

    Args:
        db (Db): Контейнер репозиториев.
        user (UserModel): Текущий пользователь-владелец плана.
        data (CreateDayDTO): Данные создаваемого дня тренировки.

    Returns:
        str | None: Текст ошибки при неудаче, иначе ``None``.
    """
    plan = await db.workout.get_plan_by_id(data.plan_id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if plan.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    workout_day = await db.workout.create_workday(WorkoutDayModel(**data.model_dump()))
    return workout_day

# @plans_router.get("/{plan_id}")
# async def get_plan(db: DbDep, plan_id: int):
#     """Получить тренировочный план по идентификатору."""
#     return db.workout.get_plan_by_id(plan_id)


# @plans_router.get("/plan_full/{plan_id}")
# async def get_full_plan(db: DbDep, plan_id: int):
#     """Получить полный тренировочный план (с днями и упражнениями) по идентификатору."""
#     return db.workout.get_full_plan_by_id(plan_id)

@plans_router.post("/add-exercise-to-day")
async def add_exercise_to_workout_day(db: DbDep, user: UserCookieDep, data: AddExerciseDTO) -> dict[str, str]:
    """Добавить упражнение в день тренировки.

    Args:
        db (Db): Контейнер репозиториев.
        data (AddExerciseDTO): Связь упражнения с днём и его параметры.

    Returns:
        dict[str, str]: Сообщение об успехе либо об ошибке (день/упражнение не найдены).
    """ 
    plan = await db.workout.get_plan_by_day_id(data.day_id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if plan.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    workout_day = await db.workout.get_workday_by_id(data.day_id)
    if not workout_day:
        return {"error": "День тренировки не найден"}
    
    exercise = await db.workout.get_exercise_by_id(data.  exercise_id)
    if not exercise:
        return {"error": "Упражнение не найдено"}
    
    await db.workout.add_exercise_to_workday(ExerciseInDayModel(**data.model_dump()))
    
    return {"info": f"Упражнение {exercise.name} добавлено к дню тренировки {workout_day.date}"}
