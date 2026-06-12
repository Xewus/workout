import datetime as dt

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums.system import TableName

from .._base import Base
from .users import UserModel


class ExerciseModel(Base):
    """Модель упражнения для хранения данных об упражнениях в базе данных."""
    __tablename__ = TableName.EXERCISE

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True, comment="Название упражнения")
    description: Mapped[str] = mapped_column(comment="Описание упражнения")
    image_path: Mapped[str | None] = mapped_column(comment="Путь к файлу на сервере")
    video_url: Mapped[str | None] = mapped_column(comment="URL видео с демонстрацией упражнения")


class WorkoutPlanModel(Base):
    """Модель тренировочного плана для хранения данных о тренировочных планах в базе данных."""
    __tablename__ = TableName.WORKOUT_PLAN

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(UserModel.id))

    title: Mapped[str] = mapped_column(comment="Название программы")
    description: Mapped[str] = mapped_column(comment="Описание программы")

class WorkoutDayModel(Base):
    """Модель дня тренировки для хранения данных о днях тренировок в базе данных и включения в тренировочный план."""
    __tablename__ = TableName.WORKOUT_DAY
    __table_args__ = (UniqueConstraint("plan_id", "date", name="uc_plan_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey(WorkoutPlanModel.id))

    date: Mapped[dt.date] = mapped_column(comment="Конкретная дата тренировки")


class ExerciseInDayModel(Base):
    """Модель для хранения данных о том, какие упражнения входят в конкретный день тренировки и их параметры."""
    __tablename__ = TableName.EXERCISE_IN_DAY

    id: Mapped[int] = mapped_column(primary_key=True)
    day_id: Mapped[int] = mapped_column(ForeignKey(WorkoutDayModel.id), comment="ID дня тренировки")
    exercise_id: Mapped[int] = mapped_column(ForeignKey(ExerciseModel.id), comment="ID упражнения")

    place_in_day: Mapped[int] = mapped_column(comment="Порядковый номер упражнения в дне тренировки")
    sets: Mapped[int] = mapped_column(comment="Количество подходов")
    reps: Mapped[int] = mapped_column(comment="Количество повторений в подходе")
    weight_kg: Mapped[int | None] = mapped_column(comment="Вес отягощения в килограммах (если применимо)")
    pause: Mapped[int | None] = mapped_column(comment="Длительность паузы между подходами в секундах")
