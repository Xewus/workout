from fastapi import APIRouter

from .exercises import exercises_router
from .plans import plans_router
from .users import router as users_router

router = APIRouter(prefix="/views")
router.include_router(exercises_router, prefix="/exercises")
router.include_router(plans_router, prefix="/plans")
router.include_router(users_router, prefix="/users")
