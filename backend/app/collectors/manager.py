import asyncio
import logging
from typing import List, Dict, Any, Optional
from app.collectors.base import RawPaper, BaseCollector
from app.collectors.openalex import OpenAlexCollector
from app.collectors.semanticscholar import SemanticScholarCollector
from app.collectors.crossref import CrossrefCollector
from app.collectors.arxiv import ArxivCollector
from app.collectors.pubmed import PubmedCollector
from app.collectors.crawler import ResearchWebCrawler

logger = logging.getLogger("research_scope.collectors.manager")
COLLECTOR_TIMEOUT_SECONDS = 45.0


class CollectorManager:
    """
    Coordinates and parallelizes requests across multiple scholarly APIs
    and the web crawler.
    """

    def __init__(self):
        self.collectors: Dict[str, BaseCollector] = {
            "openalex": OpenAlexCollector(),
            "semanticscholar": SemanticScholarCollector(),
            "crossref": CrossrefCollector(),
            "arxiv": ArxivCollector(),
            "pubmed": PubmedCollector(),
            "crawler": ResearchWebCrawler(),
        }

    async def collect_all(
        self,
        query: str,
        keywords: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        limit_per_source: int = 15,
    ) -> Dict[str, Any]:
        """
        Runs enabled collectors concurrently and returns combined papers + source counts.
        """
        active_sources = sources if sources else list(self.collectors.keys())
        source_names = []
        tasks = []

        async def fetch_source(collector_instance):
            try:
                # Allow time for slower scholarly APIs and multi-request collectors such as PubMed.
                return await asyncio.wait_for(
                    asyncio.to_thread(
                        collector_instance.search_sync,
                        query,
                        keywords,
                        limit_per_source
                    ),
                    timeout=COLLECTOR_TIMEOUT_SECONDS
                )
            except asyncio.TimeoutError:
                logger.warning(
                    "Collector '%s' timed out after %.0fs",
                    collector_instance.source_name,
                    COLLECTOR_TIMEOUT_SECONDS,
                )
                return []
            except Exception as e:
                logger.error("Collector '%s' raised exception: %s", collector_instance.source_name, e)
                return []

        for name in active_sources:
            collector = self.collectors.get(name.lower().strip())
            if collector:
                tasks.append(fetch_source(collector))
                source_names.append(collector.source_name)

        logger.info("Executing parallel threaded research collection across %d sources: %s", len(tasks), source_names)
        results = await asyncio.gather(*tasks)

        all_papers: List[RawPaper] = []
        source_breakdown: Dict[str, int] = {s: 0 for s in source_names}

        for source_name, papers_list in zip(source_names, results):
            if isinstance(papers_list, list):
                source_breakdown[source_name] = len(papers_list)
                all_papers.extend(papers_list)

        logger.info("Total raw papers collected: %d. Breakdown: %s", len(all_papers), source_breakdown)
        return {
            "papers": all_papers,
            "breakdown": source_breakdown,
            "total_raw": len(all_papers),
        }
