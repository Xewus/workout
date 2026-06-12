from __future__ import annotations

import datetime as dt
from typing import Any, Mapping, Self, Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .._base import _DbConnector
from ..models.workout import WorkoutPlanModel, WorkoutDayModel, ExerciseModel, ExerciseInDayModel


class WorkoutCRUD(_DbConnector):
    def create_plan(self: Self, plan: WorkoutPlanModel) -> str | None:
        with self.connect() as db:
            db.add(plan)
            try:
                db.commit()
                db.refresh(plan)
            except IntegrityError:
                db.rollback()
                return "Ошибка при создании плана тренировок."
        return None
    
    def get_plans(self: Self, offset: int = 0, limit: int = 10, user_id: int | None = None) -> Sequence[WorkoutPlanModel]:
        with self.connect() as db:
            query = select(WorkoutPlanModel).order_by(WorkoutPlanModel.title).offset(offset).limit(limit)
            if user_id is not None:
                query = query.where(WorkoutPlanModel.user_id == user_id)
            
            return db.execute(query).scalars().all()

    # def get_plan_by_id(self: Self, plan_id: int) -> WorkoutPlanModel | None:
    #     with self.connect() as db:
    #         result = db.execute(select(WorkoutPlanModel).where(WorkoutPlanModel.id == plan_id).limit(1))
    #         return result.scalar_one_or_none()

    def get_full_plan_by_id(self: Self, plan_id: int) -> Mapping[str, object] | None:
        """Получить полный тренировочный план (с днями и упражнениями) по идентификатору."""
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
        with self.connect() as db:
            result: Sequence[tuple[
                WorkoutPlanModel, WorkoutDayModel | None, ExerciseInDayModel | None, ExerciseModel | None]] = db.execute(stmt).all() # pyright: ignore[reportAssignmentType]
            if not result:
                return None
            
            print(result)
            plan_data = {
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

    def create_workday(self: Self, workout_day: WorkoutDayModel) -> str | None:
        with self.connect() as db:
            db.add(workout_day)
            try:
                db.commit()
                db.refresh(workout_day)
            except Exception:
                db.rollback()
                return "Агтпка"
        return None

    def get_day(self: Self, plan_id: int, date: dt.date) -> Mapping[str, Any]:
        """Получить список упражнений для дня тренировки по идентификатору плана и дате."""
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

        with self.connect() as db:
            rows: Sequence[tuple[
                WorkoutDayModel, ExerciseInDayModel | None, ExerciseModel
            ]] = db.execute(stmt).all() # pyright: ignore[reportAssignmentType]

            if not rows:
                return {}
            
            result = {
                "day_id": rows[0][0].id,
                "date": rows[0][0].date.isoformat(),
                "exercises": [],
            }
            for _, ex_day, ex in rows:
                print(_, ex_day, ex)
                result["exercises"].append(ex.dict())
            
            return result


    def create_exercise(self: Self, exercise: ExerciseModel) -> str | None:
        with self.connect() as db:
            db.add(exercise)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                return "Упражнение с таким названием уже существует."
            db.refresh(exercise)
        return None
    
    def get_exercises(self: Self, offset: int = 0, limit: int = 10) -> Sequence[ExerciseModel]:
        with self.connect() as db:
            result = db.execute(select(ExerciseModel).order_by(ExerciseModel.name).offset(offset).limit(limit))
            return result.scalars().all()

    def get_exercise_by_id(self: Self, exercise_id: int) -> ExerciseModel | None:
        with self.connect() as db:
            result = db.execute(select(ExerciseModel).where(ExerciseModel.id == exercise_id).limit(1))
            return result.scalar_one_or_none()

    def search_exercise_by_name(self: Self, string: str) -> Sequence[ExerciseModel]:
        string = f"%{string.strip().lower()}%"
        with self.connect() as db:
            result = db.execute(select(ExerciseModel).where(ExerciseModel.name.like(string)))
            return result.scalars().all()


    def update_workday(self: Self, workout_day: WorkoutDayModel) -> WorkoutDayModel:
        with self.connect() as db:
            db.merge(workout_day)
            db.commit()
            db.refresh(workout_day)
        return workout_day
    
    def get_workday_by_id(self: Self, workday_id: int) -> WorkoutDayModel | None:
        with self.connect() as db:
            result = db.execute(select(WorkoutDayModel).where(WorkoutDayModel.id == workday_id).limit(1))
            return result.scalar_one_or_none()

    def add_exercise_to_workday(self: Self, exercise: ExerciseInDayModel) -> str | None:
        with self.connect() as db:
            db.add(exercise)
            try:
                db.commit()
                db.refresh(exercise)
            except Exception as e:
                db.rollback()
                return f"Ошибка при добавлении упражнения к дню тренировки: {str(e)}"
        return None