from typing import List, Optional
from datetime import date
from uuid import UUID
from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseDocument(ABC, BaseModel):
    """
    Abstract base class for representing a document.
    Inherits from ABC (Abstract Base Class) and BaseModel.
    """
    @abstractmethod
    def repr(self) -> str:
        """
        Abstract method to return a string representation of the document.

        Returns:
            str: String representation of the document.
        """
        pass


class BaseVectorDatabaseResult(ABC, BaseModel):
    """
    Abstract base class for representing a result from a vector database query.
    Inherits from ABC (Abstract Base Class) and BaseModel.
    """
    distance: float
    doc: BaseDocument


class News(BaseDocument):
    """
    Class representing a news document.
    Inherits from BaseDocument and BaseModel.
    """

    id: UUID
    title: str
    document: str
    date: date
    link: str
    author: Optional[str] = None
    categories: Optional[List[str]] = None
    snippet: Optional[str] = None
    thumbnail_alt: Optional[str] = None
    thumbnail_link: Optional[str] = None

    def repr(self, order: Optional[int] = None):
        """
        Return a string representation of the news document.

        Args:
            order (Optional[int]): The order of the news document.

        Returns:
            str: String representation of the news document.
        """
        _start_char = "\t" if order else ""
        _firstline = f"\n<noticia_{order}>\n" if order else ""
        _lastline = f"</noticia_{order}>" if order else ""
        return (
            f"{_firstline}"
            f"{_start_char}<data>{self.date}</data>\n"
            f"{_start_char}<titulo>{self.title}</titulo>\n"
            f"{_start_char}<autor>{self.author}</autor>\n"
            f"{_start_char}<link>{self.link}</link>\n"
            f"{_start_char}<conteudo>{self.document}</conteudo>\n"
            f"{_lastline}"
        )


class VectorDatabaseNewsResult(BaseVectorDatabaseResult):
    """
    Class representing a result from a vector database query for news documents.
    Inherits from BaseVectorDatabaseResult.
    """
    pass
