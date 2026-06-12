from collections.abc import Generator
from contextlib import contextmanager
from typing import Self

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    def dict(self: Self) -> dict:
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


class _DbConnector:
    def __init__(self: Self, engine: Engine) -> None:
        self.engine = engine
        return None
    
    @contextmanager
    def connect(self: Self) -> Generator[Session]:
        with Session(self.engine) as session:
            yield session
