from __future__ import annotations

import datetime as dt
from typing import Any, Mapping, Self, Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .._base import _DbConnector
from ..models.workout import WorkoutPlanModel, WorkoutDayModel, ExerciseModel, ExerciseInDayModel


class WorkoutCRUD(_DbConnector):
    """Асинхронные операции с планами, днями и упражнениями тренировок."""

    async def create_plan(self: Self, plan: WorkoutPlanModel) -> str | None:
        """Сохранить новый тренировочный план.

        Args:
            plan (WorkoutPlanModel): План для добавления в БД.

        Returns:
            str | None: Текст ошибки при нарушении целостности,
                иначе ``None`` при успешном создании.
        """
        async with self.connect() as db:
            db.add(plan)
            try:
                await db.commit()
                await db.refresh(plan)
            except IntegrityError:
                await db.rollback()
                return "Ошибка при создании плана тренировок."
        return None

    async def get_plans(self: Self, offset: int = 0, limit: int = 10, user_id: int | None = None) -> Sequence[WorkoutPlanModel]:
        """Получить список тренировочных планов с пагинацией.

        Args:
            offset (int): Смещение выборки.
            limit (int): Максимальное число планов в выборке.
            user_id (int | None): Если задан, выбираются только планы
                этого пользователя.

        Returns:
            Sequence[WorkoutPlanModel]: Планы, отсортированные по названию.
        """
        async with self.connect() as db:
            query = select(WorkoutPlanModel).order_by(WorkoutPlanModel.title).offset(offset).limit(limit)
            if user_id is not None:
                query = query.where(WorkoutPlanModel.user_id == user_id)

            return (await db.execute(query)).scalars().all()

    # def get_plan_by_id(self: Self, plan_id: int) -> WorkoutPlanModel | None:
    #     with self.connect() as db:
    #         result = db.execute(select(WorkoutPlanModel).where(WorkoutPlanModel.id == plan_id).limit(1))
    #         return result.scalar_one_or_none()

    async def get_full_plan_by_id(self: Self, plan_id: int) -> Mapping[str, object] | None:
        """Получить полный тренировочный план (с днями и упражнениями) по идентификатору.

        Args:
            plan_id (int): Идентификатор тренировочного плана.

        Returns:
            Mapping[str, object] | None: Словарь с данными плана и
                вложенными днями/упражнениями, либо ``None``, если план
                не найден.
        """
        # Один JOIN-запрос вытягивает план вместе со всеми его днями и упражнениями;
        # дальше плоские строки сворачиваются в иерархию план -> дни -> упражнения.
        stmt = select(
            WorkoutPlanModel,
            WorkoutDayModel,
            ExerciseInDayModel,
            ExerciseModel,
        ).outerjoin(
            WorkoutDayModel, WorkoutDayModel.plan_id == WorkoutPlanModel.id
        ).outerjoin(
            ExerciseInDayModel, ExerciseInDayModel.day_id == WorkoutDayModel.id
        ).outerjoin(
            ExerciseModel, ExerciseModel.id == ExerciseInDayModel.exercise_id
        ).where(WorkoutPlanModel.id == plan_id
        ).order_by(WorkoutDayModel.date, ExerciseInDayModel.place_in_day)
        async with self.connect() as db:
            result: Sequence[tuple[
                WorkoutPlanModel, WorkoutDayModel | None, ExerciseInDayModel | None, ExerciseModel | None]] = (await db.execute(stmt)).all() # pyright: ignore[reportAssignmentType]
            if not result:
                return None

            print(result)
            plan_data: dict[str, Any] = {
                "id": plan_id,
                "title": result[0][0].title,
                "description": result[0][0].description,
                "days": {}
            }
            if result[0][1] is None:  # Если нет дней тренировки, возвращаем только данные плана
                return plan_data

            for _, day, exercise_in_day, exercise in result:
                print(day)
                if day is None:
                    break  # Если день тренировки отсутствует, прекращаем обработку)

                day_date = day.date.isoformat()
                if day_date not in plan_data["days"]:
                    plan_data["days"][day_date] = {"exercises": []} # Инициализируем день, если его еще нет в словаре

                if exercise_in_day is None or exercise is None:
                    continue  # Если упражнение отсутствует, переходим к следующему дню тренировки

                plan_data["days"][day_date]["exercises"].append(
                    {
                    "name": exercise.name,
                    "reps": exercise_in_day.reps,
                    "sets": exercise_in_day.sets,
                })
            return plan_data

    async def create_workday(self: Self, workout_day: WorkoutDayModel) -> str | None:
        """Создать день тренировки в рамках плана.

        Args:
            workout_day (WorkoutDayModel): День тренировки для сохранения.

        Returns:
            str | None: Текст ошибки при неудаче, иначе ``None``.
        """
        async with self.connect() as db:
            db.add(workout_day)
            try:
                await db.commit()
                await db.refresh(workout_day)
            except Exception:
                await db.rollback()
                return "Агтпка"
        return None

    async def get_day(self: Self, plan_id: int, date: dt.date) -> Mapping[str, Any]:
        """Получить список упражнений для дня тренировки по идентификатору плана и дате.

        Args:
            plan_id (int): Идентификатор тренировочного плана.
            date (dt.date): Дата дня тренировки.

        Returns:
            Mapping[str, Any]: Словарь с данными дня и списком упражнений;
                пустой словарь, если день не найден.
        """
        stmt = select(
            WorkoutDayModel,
            ExerciseInDayModel,
            ExerciseModel
        ).outerjoin(
            ExerciseInDayModel, ExerciseInDayModel.day_id == WorkoutDayModel.id
        ).outerjoin(
            ExerciseModel, ExerciseInDayModel.exercise_id == ExerciseModel.id
        ).where(
            WorkoutDayModel.plan_id == plan_id, WorkoutDayModel.date == date
        ).order_by(ExerciseInDayModel.place_in_day)

        async with self.connect() as db:
            rows: Sequence[tuple[
                WorkoutDayModel, ExerciseInDayModel | None, ExerciseModel
            ]] = (await db.execute(stmt)).all() # pyright: ignore[reportAssignmentType]

            if not rows:
                return {}

            result: dict[str, Any] = {
                "day_id": rows[0][0].id,
                "date": rows[0][0].date.isoformat(),
                "exercises": [],
            }
            for _, ex_day, ex in rows:
                print(_, ex_day, ex)
                result["exercises"].append(ex.dict())

            return result


    async def create_exercise(self: Self, exercise: ExerciseModel) -> str | None:
        """Сохранить новое упражнение.

        Args:
            exercise (ExerciseModel): Упражнение для добавления в БД.

        Returns:
            str | None: Текст ошибки при конфликте уникальности,
                иначе ``None``.
        """
        async with self.connect() as db:
            db.add(exercise)
            try:
                await db.commit()
            except IntegrityError:
                await db.rollback()
                return "Упражнение с таким названием уже существует."
            await db.refresh(exercise)
        return None

    async def get_exercises(self: Self, offset: int = 0, limit: int = 10) -> Sequence[ExerciseModel]:
        """Получить список упражнений с пагинацией.

        Args:
            offset (int): Смещение выборки.
            limit (int): Максимальное число упражнений в выборке.

        Returns:
            Sequence[ExerciseModel]: Упражнения, отсортированные по названию.
        """
        async with self.connect() as db:
            result = await db.execute(select(ExerciseModel).order_by(ExerciseModel.name).offset(offset).limit(limit))
            return result.scalars().all()

    async def get_exercise_by_id(self: Self, exercise_id: int) -> ExerciseModel | None:
        """Получить упражнение по идентификатору.

        Args:
            exercise_id (int): Идентификатор упражнения.

        Returns:
            ExerciseModel | None: Найденное упражнение либо ``None``.
        """
        async with self.connect() as db:
            result = await db.execute(select(ExerciseModel).where(ExerciseModel.id == exercise_id).limit(1))
            return result.scalar_one_or_none()

    async def search_exercise_by_name(self: Self, string: str) -> Sequence[ExerciseModel]:
        """Найти упражнения по подстроке названия (регистронезависимо).

        Args:
            string (str): Поисковая подстрока названия.

        Returns:
            Sequence[ExerciseModel]: Упражнения, чьё название содержит подстроку.
        """
        string = f"%{string.strip().lower()}%"
        async with self.connect() as db:
            result = await db.execute(select(ExerciseModel).where(ExerciseModel.name.like(string)))
            return result.scalars().all()


    async def update_workday(self: Self, workout_day: WorkoutDayModel) -> WorkoutDayModel:
        """Обновить (слить) день тренировки.

        Args:
            workout_day (WorkoutDayModel): День тренировки с новыми данными.

        Returns:
            WorkoutDayModel: Актуальный объект дня тренировки после слияния.
        """
        async with self.connect() as db:
            workout_day = await db.merge(workout_day)
            await db.commit()
            await db.refresh(workout_day)
        return workout_day

    async def get_workday_by_id(self: Self, workday_id: int) -> WorkoutDayModel | None:
        """Получить день тренировки по идентификатору.

        Args:
            workday_id (int): Идентификатор дня тренировки.

        Returns:
            WorkoutDayModel | None: Найденный день тренировки либо ``None``.
        """
        async with self.connect() as db:
            result = await db.execute(select(WorkoutDayModel).where(WorkoutDayModel.id == workday_id).limit(1))
            return result.scalar_one_or_none()

    async def add_exercise_to_workday(self: Self, exercise: ExerciseInDayModel) -> str | None:
        """Добавить упражнение в конкретный день тренировки.

        Args:
            exercise (ExerciseInDayModel): Связь упражнения с днём тренировки
                и его параметры (подходы, повторения и т. д.).

        Returns:
            str | None: Текст ошибки при неудаче, иначе ``None``.
        """
        async with self.connect() as db:
            db.add(exercise)
            try:
                await db.commit()
                await db.refresh(exercise)
            except Exception as e:
                await db.rollback()
                return f"Ошибка при добавлении упражнения к дню тренировки: {str(e)}"
        return None
