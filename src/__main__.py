from collections.abc import AsyncGenerator, Awaitable, Callable
import datetime as dt
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.api import main_router as router
from src.config import config


templates = Jinja2Templates(directory=Path("src/templates"))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(
    title=config.TITLE,
    description=config.DESCRIPTION,
    version=config.VERSION,
    lifespan=lifespan
)

app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")

setattr(app, "images_dir", config.UPLOAD_DIR)
setattr(app, "templates", templates)



@app.middleware("http")
async def add_process_404(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Промежуточное ПО для обработки 404 ошибок и отображения кастомной страницы."""
    try:
        response = await call_next(request)
    except Exception as e:
        print(f"Error processing request: {e}")
        return templates.TemplateResponse("500.html", {"request": request}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if response.status_code == 401:
        return templates.TemplateResponse("401.html", {"request": request}, status_code=response.status_code)

    if response.status_code == 404:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=response.status_code)
    
    if response.status_code >= 500:
        return templates.TemplateResponse("500.html", {"request": request}, status_code=response.status_code)

    return response

def format_date_filter(value: str) -> str:
    """Переформатирование даты в текстовый вид.

    Args:
        value (str): Дата в формате ISO.

    Returns:
        str: Текстовое представление даты.
    """
    d = dt.date.fromisoformat(value)
    months = ["янв","фев","мар","апр","май","июн","июл","авг","сен","окт","ноя","дек"]
    days   = ["пн","вт","ср","чт","пт","сб","вс"]
    return f"{days[d.weekday()]}, {d.day} {months[d.month - 1]}"


templates.env.filters["basename"] = lambda p: Path(p).name
templates.env.filters["format_date"] = format_date_filter

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
