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

exercises_router = APIRouter()

@exercises_router.post("/create")
async def add_exercise(
    request: ApiRequest,
    db: DbDep,
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    image: Annotated[UploadFile | None, File()] = None,
    video_url: Annotated[str | None, Form()] = None,
):
    """Добавляет новое упражнение, обрабатывая загрузку изображения."""
    exercise = ExerciseModel(name=name, description=description, video_url=video_url)
    if image and image.filename:
        filename = f"{exercise.name}_{uuid4()}.{image.filename.split('.')[-1]}"
        file_path = request.app.images_dir / filename
        if file_path.exists():
            raise ValueError("Файл с таким именем уже существует")

        with file_path.open("wb") as buffer:
            buffer.write(await image.read())
        exercise.image_path = str(file_path)

    # Добавляем упражнение в базу данных
    err = db.workout.create_exercise(exercise)
    if err:
        raise HTTPException(status_code=400, detail=err)

    return {"info": f"Упражнение {exercise.name} добавлено с ID {exercise.id}"}

@exercises_router.get("/search")
def search_exercise(db: DbDep, string: Annotated[str, Query()]):
    print(string)
    return db.workout.search_exercise_by_name(string)


@exercises_router.get("")
async def list_exercises(*, db: DbDep, offset: int = 0, limit: int = 10):
    """Получить список упражнений."""
    exercises = db.workout.get_exercises(offset=offset, limit=limit)
    return exercises

@exercises_router.get("/{exercise_id}")
async def get_exercise(db: DbDep, exercise_id: int):
    """Получить упражнение по идентификатору."""
    exercise = db.workout.get_exercise_by_id(exercise_id)
    if not exercise:
        return {"error": "Упражнение не найдено"}
    return exercise
