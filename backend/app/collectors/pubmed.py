import logging
from typing import List, Optional
import requests
from app.collectors.base import BaseCollector, RawPaper
from app.core.config import settings

logger = logging.getLogger("research_scope.collectors.pubmed")


class PubmedCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "pubmed"

    def search_sync(self, query: str, keywords: Optional[List[str]] = None, limit: int = 15) -> List[RawPaper]:
        papers: List[RawPaper] = []
        try:
            # Clean and form PubMed term
            clean_term = query.replace('"', '')
            if keywords and len(keywords) > 0:
                clean_term += f" AND {keywords[0]}"

            # 1. ESearch
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": clean_term,
                "retmode": "json",
                "retmax": min(limit, 20),
                "sort": "relevance",
            }
            if settings.PUBMED_API_KEY:
                search_params["api_key"] = settings.PUBMED_API_KEY

            headers = {"User-Agent": settings.CRAWLER_USER_AGENT}
            search_res = requests.get(search_url, params=search_params, headers=headers, timeout=5)
            if search_res.status_code != 200:
                logger.warning("PubMed ESearch returned %s", search_res.status_code)
                return papers

            search_data = search_res.json()
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            if not id_list:
                logger.info("No PubMed IDs matched query: %s", query[:30])
                return papers

            # 2. ESummary
            summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            summary_params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "json",
            }
            if settings.PUBMED_API_KEY:
                summary_params["api_key"] = settings.PUBMED_API_KEY

            summary_res = requests.get(summary_url, params=summary_params, headers=headers, timeout=5)
            if summary_res.status_code != 200:
                logger.warning("PubMed ESummary returned %s", summary_res.status_code)
                return papers

            summary_data = summary_res.json().get("result", {})

            for pmid in id_list:
                item = summary_data.get(pmid)
                if not item or not isinstance(item, dict):
                    continue

                title = item.get("title", "").rstrip(".")
                if not title:
                    continue

                authors = [a.get("name") for a in item.get("authors", []) if a.get("name")]
                venue = item.get("source")

                # Extract year
                pubdate = item.get("pubdate", "")
                year = None
                if pubdate and len(pubdate) >= 4:
                    try:
                        year = int(pubdate[:4])
                    except ValueError:
                        year = None

                # Extract DOI
                doi = None
                for article_id in item.get("articleids", []):
                    if article_id.get("idtype") == "doi":
                        doi = article_id.get("value")
                        break

                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

                paper = RawPaper(
                    title=title.strip(),
                    abstract=None,  # ESummary does not include full abstract; will be enriched or title-analyzed
                    authors=authors,
                    year=year,
                    venue=venue,
                    citations=0,
                    source=self.source_name,
                    url=url,
                    doi=doi,
                    keywords=[venue] if venue else [],
                )
                papers.append(paper)

            logger.info("PubMed fetched %d papers for query: '%s'", len(papers), query[:40])
        except Exception as e:
            logger.error("Error collecting from PubMed: %s", e)

        return papers
