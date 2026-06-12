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
    """Создать новый тренировочный план."""
    model = WorkoutPlanModel(title=data.title, description=data.description or "", user_id=user.id)
    if err := db.workout.create_plan(model):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    return model.id

# @plans_router.get("/plans")
# async def list_plans(*, db: DbDep, user: Annotated[UserModel, Depends(get_cookie_user)], only_mine: bool = False, offset: int = 0, limit: int = 10):
#     """Получить список тренировочных планов."""
#     user_id = user.id if only_mine else None
#     plans = db.workout.get_plans(offset=offset, limit=limit, user_id=user_id)
#     return plans


@plans_router.post("/workout_day")
async def create_workout_day(db: DbDep, data: CreateDayDTO):
    """Создать новый день тренировки для конкретного плана."""
    workout_day = db.workout.create_workday(WorkoutDayModel(**data.model_dump()))
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
async def add_exercise_to_workout_day(db: DbDep, data: AddExerciseDTO):
    workout_day = db.workout.get_workday_by_id(data.day_id)
    print(f"{workout_day=}")
    if not workout_day:
        return {"error": "День тренировки не найден"}
    
    exercise = db.workout.get_exercise_by_id(data.  exercise_id)
    print(f"{exercise=}")
    if not exercise:
        return {"error": "Упражнение не найдено"}
    
    db.workout.add_exercise_to_workday(ExerciseInDayModel(**data.model_dump()))
    
    return {"info": f"Упражнение {exercise.name} добавлено к дню тренировки {workout_day.date}"}
