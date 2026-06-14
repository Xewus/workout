from fastapi import APIRouter

from src.core.typings import ApiRequest

from .v1 import router as v1_router
from .views import router as views_router

api_router = APIRouter(prefix="/api")
api_router.include_router(v1_router)
api_router.include_router(views_router, include_in_schema=False)

main_router = APIRouter()

@main_router.get("/", include_in_schema=False)
def index(request: ApiRequest):
    return request.app.templates.TemplateResponse("index.html", {"request": request})

@main_router.get(".well-known/appspecific/com.chrome.devtools.json", include_in_schema=False)
def devtools():
    return {}

main_router.include_router(api_router)
