import logging
from typing import List, Optional
import requests
from app.collectors.base import BaseCollector, RawPaper
from app.core.config import settings

logger = logging.getLogger("research_scope.collectors.openalex")


class OpenAlexCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "openalex"

    def _reconstruct_abstract(self, inverted_index: Optional[dict]) -> Optional[str]:
        """Reconstructs abstract string from OpenAlex inverted index representation."""
        if not inverted_index or not isinstance(inverted_index, dict):
            return None
        try:
            word_positions = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort(key=lambda x: x[0])
            return " ".join(w for _, w in word_positions)
        except Exception:
            return None

    def search_sync(self, query: str, keywords: Optional[List[str]] = None, limit: int = 15) -> List[RawPaper]:
        papers: List[RawPaper] = []
        try:
            search_query = query
            if keywords and len(keywords) > 0:
                search_query += " " + " ".join(keywords[:3])

            params = {
                "search": search_query,
                "per-page": min(limit, 25),
                "sort": "relevance_score:desc",
            }
            if settings.CROSSREF_MAILTO:
                params["mailto"] = settings.CROSSREF_MAILTO

            headers = {"User-Agent": settings.CRAWLER_USER_AGENT}
            if settings.OPENALEX_API_KEY:
                headers["Authorization"] = f"Bearer {settings.OPENALEX_API_KEY}"

            response = requests.get(
                "https://api.openalex.org/works",
                params=params,
                headers=headers,
                timeout=6,
            )
            if response.status_code != 200:
                logger.warning("OpenAlex API returned status %s: %s", response.status_code, response.text[:200])
                return papers

            data = response.json()
            results = data.get("results", [])

            for item in results:
                title = item.get("title")
                if not title:
                    continue

                abstract = self._reconstruct_abstract(item.get("abstract_inverted_index"))
                
                # Extract authors
                authors = []
                for authorship in item.get("authorships", []):
                    author_obj = authorship.get("author", {})
                    name = author_obj.get("display_name")
                    if name:
                        authors.append(name)

                # Extract venue / journal
                venue = None
                primary_loc = item.get("primary_location") or {}
                source_obj = primary_loc.get("source") or {}
                if source_obj.get("display_name"):
                    venue = source_obj.get("display_name")

                # Extract keywords / concepts
                extracted_keywords = []
                for concept in item.get("concepts", []):
                    cname = concept.get("display_name")
                    if cname:
                        extracted_keywords.append(cname)

                paper = RawPaper(
                    title=title.strip(),
                    abstract=abstract,
                    authors=authors,
                    year=item.get("publication_year"),
                    venue=venue,
                    citations=item.get("cited_by_count", 0) or 0,
                    source=self.source_name,
                    url=item.get("doi") or item.get("id"),
                    doi=item.get("doi", "").replace("https://doi.org/", "") if item.get("doi") else None,
                    keywords=extracted_keywords[:5],
                )
                papers.append(paper)

            logger.info("OpenAlex fetched %d papers for query: '%s'", len(papers), query[:40])
        except Exception as e:
            logger.error("Error collecting from OpenAlex: %s", e)

        return papers
