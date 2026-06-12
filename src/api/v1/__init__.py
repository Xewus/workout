from fastapi import APIRouter

from .exercises import exercises_router
from .plans import plans_router
from .users import router as users_router

router = APIRouter()
router.include_router(exercises_router, prefix="/exercises", tags=["EXERCISES"])
router.include_router(plans_router, prefix="/plans", tags=["PLANS"])
router.include_router(users_router, prefix="/users", tags=["USERS"])
