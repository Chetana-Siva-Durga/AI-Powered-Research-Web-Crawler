import logging
from typing import List, Optional
import requests
from app.collectors.base import BaseCollector, RawPaper
from app.core.config import settings

logger = logging.getLogger("research_scope.collectors.crossref")


class CrossrefCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "crossref"

    def search_sync(self, query: str, keywords: Optional[List[str]] = None, limit: int = 15) -> List[RawPaper]:
        papers: List[RawPaper] = []
        try:
            search_query = query
            if keywords and len(keywords) > 0:
                search_query += " " + " ".join(keywords[:2])

            params = {
                "query": search_query,
                "rows": min(limit, 20),
                "mailto": settings.CROSSREF_MAILTO,
                "sort": "relevance",
            }
            headers = {"User-Agent": f"ResearchScope/1.0 (mailto:{settings.CROSSREF_MAILTO})"}

            response = requests.get(
                "https://api.crossref.org/works",
                params=params,
                headers=headers,
                timeout=6,
            )
            if response.status_code != 200:
                logger.warning("Crossref returned status %s: %s", response.status_code, response.text[:200])
                return papers

            data = response.json()
            items = data.get("message", {}).get("items", [])

            for item in items:
                title_list = item.get("title", [])
                if not title_list or not title_list[0]:
                    continue
                title = title_list[0]

                # Author names
                authors = []
                for author in item.get("author", []):
                    given = author.get("given", "")
                    family = author.get("family", "")
                    full_name = f"{given} {family}".strip()
                    if full_name:
                        authors.append(full_name)

                # Publication year
                pub_year = None
                published = item.get("published-print") or item.get("published-online") or item.get("issued")
                if published and "date-parts" in published and published["date-parts"]:
                    parts = published["date-parts"][0]
                    if parts and len(parts) > 0 and parts[0]:
                        try:
                            pub_year = int(parts[0])
                        except (ValueError, TypeError):
                            pub_year = None

                # Venue / container title
                container_titles = item.get("container-title", [])
                venue = container_titles[0] if container_titles else None

                doi = item.get("DOI")
                url = item.get("URL") or (f"https://doi.org/{doi}" if doi else None)

                # Abstract clean up if present (Crossref sometimes puts JATS XML in abstract)
                abstract = item.get("abstract")
                if abstract and "<jats:p>" in abstract:
                    abstract = abstract.replace("<jats:p>", "").replace("</jats:p>", " ").strip()

                paper = RawPaper(
                    title=title.strip(),
                    abstract=abstract,
                    authors=authors,
                    year=pub_year,
                    venue=venue,
                    citations=item.get("is-referenced-by-count", 0) or 0,
                    source=self.source_name,
                    url=url,
                    doi=doi,
                    keywords=item.get("subject", [])[:5],
                )
                papers.append(paper)

            logger.info("Crossref fetched %d papers for query: '%s'", len(papers), query[:40])
        except Exception as e:
            logger.error("Error collecting from Crossref: %s", e)

        return papers
