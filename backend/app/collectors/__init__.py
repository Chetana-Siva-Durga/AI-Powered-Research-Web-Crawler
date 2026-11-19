from app.collectors.base import BaseCollector, RawPaper
from app.collectors.openalex import OpenAlexCollector
from app.collectors.semanticscholar import SemanticScholarCollector
from app.collectors.crossref import CrossrefCollector
from app.collectors.arxiv import ArxivCollector
from app.collectors.pubmed import PubmedCollector
from app.collectors.crawler import ResearchWebCrawler
from app.collectors.manager import CollectorManager

__all__ = [
    "BaseCollector",
    "RawPaper",
    "OpenAlexCollector",
    "SemanticScholarCollector",
    "CrossrefCollector",
    "ArxivCollector",
    "PubmedCollector",
    "ResearchWebCrawler",
    "CollectorManager",
]
