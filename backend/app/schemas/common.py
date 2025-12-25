from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel

T = TypeVar('T')


class Message(BaseModel):
    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
