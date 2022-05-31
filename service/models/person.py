from datetime import date

from uuid import UUID
from typing import Optional
from pydantic import BaseModel

from .base import BaseOrjsonModel


class Person(BaseModel, BaseOrjsonModel.Config):
    id: UUID
    full_name: str
    birth_date: Optional[date]
