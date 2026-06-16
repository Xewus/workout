from dataclasses import dataclass

from ._base import Base, engine
from .cruds.users import UserCRUD, UserModel  # noqa: E402, F401
from .cruds.workout import WorkoutCRUD, WorkoutPlanModel, WorkoutDayModel, ExerciseModel, ExerciseInDayModel  # noqa: E402, F401


async def init_db() -> None:
    """Создать все таблицы по метаданным моделей.

    Выполняется в рамках транзакции движка, синхронный вызов
    ``create_all`` оборачивается в ``run_sync`` для совместимости
    с асинхронным движком.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@dataclass(frozen=True)
class Db:
    """Контейнер CRUD-репозиториев приложения.

    Attributes:
        workout (WorkoutCRUD): Репозиторий тренировок, планов и упражнений.
        user (UserCRUD): Репозиторий пользователей.
    """

    workout: WorkoutCRUD
    user: UserCRUD


db = Db(
    workout=WorkoutCRUD(engine),
    user=UserCRUD(engine)
)


async def get_db() -> Db:
    """Зависимость FastAPI, возвращающая общий контейнер репозиториев.

    Returns:
        Db: Разделяемый между запросами экземпляр контейнера CRUD.
    """
    return db
