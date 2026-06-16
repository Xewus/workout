from dataclasses import dataclass

from ._base import Base, engine
from .cruds.users import UserCRUD, UserModel  # noqa: E402, F401
from .cruds.workout import WorkoutCRUD, WorkoutPlanModel, WorkoutDayModel, ExerciseModel, ExerciseInDayModel  # noqa: E402, F401


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@dataclass(frozen=True)
class Db:
    workout: WorkoutCRUD
    user: UserCRUD

db = Db(
    workout=WorkoutCRUD(engine),
    user=UserCRUD(engine)
)

async def get_db() -> Db:
    return db
