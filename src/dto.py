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
    """Токен доступа, возвращаемый при аутентификации."""

    access_token: str = Field(description="JWT-токен доступа.")
    token_type: str = Field(default="bearer", description="Тип токена.")

# ####################################################### #

class CreatePlanDTO(BaseModel):
    """Модель данных для создания нового плана тренировок через API."""
    title: str = Field(description="Название программы")
    description: str | None = Field(None, description="Описание программы")

class CreateDayDTO(BaseModel):
    """Модель данных для создания дня тренировки через API."""

    date: dt.date = Field(description="Дата дня тренировки.")
    plan_id: int = Field(description="Идентификатор тренировочного плана.")


class AddExerciseDTO(BaseModel):
    """Модель данных для добавления упражнения в день тренировки через API."""

    day_id: int = Field(description="Идентификатор дня тренировки.")
    exercise_id: int = Field(description="Идентификатор упражнения.")

    place_in_day: int = Field(description="Порядковый номер упражнения в дне.")
    sets: int = Field(description="Количество подходов.")
    reps: int = Field(description="Количество повторений в подходе.")
    weight_kg: int | None = Field(description="Вес отягощения в килограммах (если применимо).")
    pause: int | None = Field(description="Длительность паузы между подходами в секундах.")