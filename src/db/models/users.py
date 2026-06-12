from sqlalchemy.orm import Mapped, mapped_column
import datetime as dt

from src.core.enums.system import TableName
from .._base import Base

class UserModel(Base):
    """Модель пользователя для хранения данных о пользователях в базе данных."""
    __tablename__ = TableName.USER

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(comment="Зашифрованый пароль")
    birth_date: Mapped[dt.date] = mapped_column(comment="Дата рождения пользователя")
    sex: Mapped[str] = mapped_column(comment="Пол пользователя: 'F' для женщин, 'M' для мужчин")
    height_cm: Mapped[int] = mapped_column(comment="Рост пользователя в сантиметрах")
    weight_kg: Mapped[int] = mapped_column(comment="Вес пользователя в килограммах")
