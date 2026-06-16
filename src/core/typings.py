from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

class API(FastAPI):
    """Приложение FastAPI с дополнительными атрибутами приложения.

    Attributes:
        images_dir (Path): Каталог для загруженных изображений.
        templates (Jinja2Templates): Движок рендеринга HTML-шаблонов.
    """

    images_dir: Path
    templates: Jinja2Templates
    

class ApiRequest(Request):
    """Запрос с уточнённым типом приложения для подсказок типов.

    Attributes:
        app (API): Экземпляр приложения с пользовательскими атрибутами.
    """

    app: API # pyright: ignore[reportIncompatibleMethodOverride]
