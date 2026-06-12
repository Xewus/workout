import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field



class UserDTO(BaseModel):
    """Модель данных для регистрации пользователя через API."""
    username: str = Field(description="Имя пользователя.")
    password: str = Field(description="Пароль пользователя.")
    birth_date: dt.date = Field(description="Дата рождения пользователя.")
    sex: Literal["F", "M"] = Field(description="Пол пользователя: 'F' для женщин, 'M' для мужчин")
    height_cm: int = Field(description="Рост пользователя в сантиметрах", ge=90, le=250)
    weight_kg: int = Field(description="Вес пользователя в килограммах", ge=30, le=300)


class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ####################################################### #

class CreatePlanDTO(BaseModel):
    """Модель данных для создания нового плана тренировок через API."""
    title: str = Field(description="Название программы")
    description: str | None = Field(None, description="Описание программы")

class CreateDayDTO(BaseModel):
    date: dt.date
    plan_id: int


class AddExerciseDTO(BaseModel):
    day_id: int
    exercise_id: int

    place_in_day: int
    sets: int
    reps: int
    weight_kg: int | None
    pause: int | None