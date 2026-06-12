from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

class API(FastAPI):
    images_dir: Path
    templates: Jinja2Templates
    

class ApiRequest(Request):
    app: API # pyright: ignore[reportIncompatibleMethodOverride]
