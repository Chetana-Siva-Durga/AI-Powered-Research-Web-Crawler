import logging
from typing import List, Optional
import requests
from app.collectors.base import BaseCollector, RawPaper
from app.core.config import settings

logger = logging.getLogger("research_scope.collectors.semanticscholar")


class SemanticScholarCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "semanticscholar"

    def search_sync(self, query: str, keywords: Optional[List[str]] = None, limit: int = 15) -> List[RawPaper]:
        papers: List[RawPaper] = []
        try:
            search_query = query
            if keywords and len(keywords) > 0:
                search_query += " " + " ".join(keywords[:2])

            params = {
                "query": search_query,
                "limit": min(limit, 20),
                "fields": "title,abstract,authors,year,venue,citationCount,url,externalIds,fieldsOfStudy",
            }

            headers = {"User-Agent": settings.CRAWLER_USER_AGENT}
            if settings.SEMANTIC_SCHOLAR_API_KEY:
                headers["x-api-key"] = settings.SEMANTIC_SCHOLAR_API_KEY

            response = requests.get(
                "https://api.semanticscholar.org/graph/v1/paper/search",
                params=params,
                headers=headers,
                timeout=6,
            )
            if response.status_code != 200:
                logger.warning("Semantic Scholar returned status %s: %s", response.status_code, response.text[:200])
                return papers

            data = response.json()
            items = data.get("data", [])

            for item in items:
                title = item.get("title")
                if not title:
                    continue

                authors = [a.get("name") for a in item.get("authors", []) if a.get("name")]
                ext_ids = item.get("externalIds") or {}
                doi = ext_ids.get("DOI")
                fields_of_study = item.get("fieldsOfStudy") or []

                paper = RawPaper(
                    title=title.strip(),
                    abstract=item.get("abstract"),
                    authors=authors,
                    year=item.get("year"),
                    venue=item.get("venue"),
                    citations=item.get("citationCount", 0) or 0,
                    source=self.source_name,
                    url=item.get("url") or (f"https://doi.org/{doi}" if doi else None),
                    doi=doi,
                    keywords=fields_of_study[:5],
                )
                papers.append(paper)

            logger.info("Semantic Scholar fetched %d papers for query: '%s'", len(papers), query[:40])
        except Exception as e:
            logger.error("Error collecting from Semantic Scholar: %s", e)

        return papers
