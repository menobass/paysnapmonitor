from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    purchases: int
    last_purchase: Optional[str]


class Store(BaseModel):
    username: str


class Ban(BaseModel):
    username: str
