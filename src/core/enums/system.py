from enum import StrEnum


class TableName(StrEnum):
    """Имена таблиц БД, используемые в ORM-моделях."""

    EXERCISE = "exercise"
    EXERCISE_IN_DAY = "exercise_in_day"
    USER = "user"
    WORKOUT_PLAN = "workout_plan"
    WORKOUT_DAY = "workout_day"
