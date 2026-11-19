import logging
from typing import List, Optional
import xml.etree.ElementTree as ET
import requests
from app.collectors.base import BaseCollector, RawPaper
from app.core.config import settings

logger = logging.getLogger("research_scope.collectors.arxiv")


class ArxivCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "arxiv"

    def search_sync(self, query: str, keywords: Optional[List[str]] = None, limit: int = 15) -> List[RawPaper]:
        papers: List[RawPaper] = []
        try:
            # Build search terms for arXiv query
            clean_query = query.replace('"', '').replace(":", " ")
            search_terms = f"all:{clean_query}"
            if keywords and len(keywords) > 0:
                search_terms += f" AND all:{keywords[0]}"

            params = {
                "search_query": search_terms,
                "start": 0,
                "max_results": min(limit, 20),
                "sortBy": "relevance",
                "sortOrder": "descending",
            }
            headers = {"User-Agent": settings.CRAWLER_USER_AGENT}

            response = requests.get(
                "http://export.arxiv.org/api/query",
                params=params,
                headers=headers,
                timeout=6,
            )
            if response.status_code != 200:
                logger.warning("arXiv API returned status %s", response.status_code)
                return papers

            # Parse Atom XML
            root = ET.fromstring(response.content)
            atom_ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

            for entry in root.findall("atom:entry", atom_ns):
                title_elem = entry.find("atom:title", atom_ns)
                summary_elem = entry.find("atom:summary", atom_ns)
                published_elem = entry.find("atom:published", atom_ns)
                id_elem = entry.find("atom:id", atom_ns)

                if title_elem is None or not title_elem.text:
                    continue

                title = title_elem.text.strip().replace("\n", " ")
                abstract = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None else None
                url = id_elem.text.strip() if id_elem is not None else None

                # Extract year from published ISO string (e.g. 2024-03-15T...)
                year = None
                if published_elem is not None and published_elem.text:
                    try:
                        year = int(published_elem.text[:4])
                    except ValueError:
                        year = None

                # Extract authors
                authors = []
                for author in entry.findall("atom:author", atom_ns):
                    name_elem = author.find("atom:name", atom_ns)
                    if name_elem is not None and name_elem.text:
                        authors.append(name_elem.text.strip())

                # Extract categories as keywords
                categories = []
                for cat in entry.findall("atom:category", atom_ns):
                    term = cat.get("term")
                    if term:
                        categories.append(term)

                # Extract DOI if present
                doi = None
                doi_elem = entry.find("arxiv:doi", atom_ns)
                if doi_elem is not None and doi_elem.text:
                    doi = doi_elem.text.strip()

                paper = RawPaper(
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    year=year,
                    venue="arXiv Preprint",
                    citations=0,
                    source=self.source_name,
                    url=url,
                    doi=doi,
                    keywords=categories[:5],
                )
                papers.append(paper)

            logger.info("arXiv fetched %d papers for query: '%s'", len(papers), query[:40])
        except Exception as e:
            logger.error("Error collecting from arXiv: %s", e)

        return papers
