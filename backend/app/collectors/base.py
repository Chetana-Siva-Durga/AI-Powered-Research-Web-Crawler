from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field


class RawPaper(BaseModel):
    title: str
    abstract: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    venue: Optional[str] = None
    citations: int = 0
    source: str = "unknown"
    url: Optional[str] = None
    doi: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)


class BaseCollector(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of the collector source (e.g., 'openalex', 'crawler')."""
        pass

    def search_sync(self, query: str, keywords: Optional[List[str]] = None, limit: int = 15) -> List[RawPaper]:
        """Synchronous search execution in thread."""
        raise NotImplementedError

    async def search(self, query: str, keywords: Optional[List[str]] = None, limit: int = 15) -> List[RawPaper]:
        """Async interface delegating to search_sync."""
        return self.search_sync(query, keywords, limit)

