from typing import Optional

from uuid import UUID
from pydantic import BaseModel

from .base import BaseOrjsonModel


class Genre(BaseModel, BaseOrjsonModel.Config):
    id: UUID
    name: str
    description: Optional[str] = ''
