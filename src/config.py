from pathlib import Path

from pydantic_settings import BaseSettings


# Папка для картинок
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
class AppConfig(BaseSettings):
    """Конфигурация приложения."""

    TITLE: str = "GymPlans"
    DESCRIPTION: str = "планировщик тренировок для всех уровней подготовки"
    VERSION: str = "0.0.1"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300
    ALGORITHM: str = "HS256"
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    TOKEN_URL: str = "api/v1/users/token"

    UPLOAD_DIR: Path = UPLOAD_DIR


config = AppConfig()
