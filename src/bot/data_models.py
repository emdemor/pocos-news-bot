from typing import List, Optional
from datetime import date
from uuid import UUID

from pydantic import BaseModel


class News(BaseModel):
    id: UUID
    title: str
    document: str
    date: date
    link: str
    author: Optional[str]
    categories: Optional[List[str]]
    snippet: Optional[str]
    thumbnail_alt: Optional[str]
    thumbnail_link: Optional[str]


class VectorDatabaseNewsResult(BaseModel):
    distance: float
    news: News
