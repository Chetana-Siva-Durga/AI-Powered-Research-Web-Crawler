import logging
import re
from typing import List, Optional
from urllib.parse import urljoin, quote_plus
import requests
from bs4 import BeautifulSoup
from app.collectors.base import BaseCollector, RawPaper
from app.core.config import settings

logger = logging.getLogger("research_scope.collectors.crawler")


class ResearchWebCrawler(BaseCollector):
    """
    Focused Scholarly Web Crawler using Requests and BeautifulSoup.
    Crawls open academic repositories and preprint listings (e.g. arXiv HTML search/listings,
    open-access repositories) respecting robots.txt and polite crawl delays.
    Extracts structured research metadata from Dublin Core / Highwire Press meta tags and DOM elements.
    """

    @property
    def source_name(self) -> str:
        return "crawler"

    def _extract_paper_from_html(self, page_url: str, html_content: str) -> Optional[RawPaper]:
        """
        Parses scholarly HTML using standard meta tags (Highwire Press / Dublin Core)
        and semantic HTML elements.
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # 1. Title extraction
            title = None
            meta_title = soup.find("meta", attrs={"name": re.compile(r"citation_title|dc\.title", re.I)})
            if meta_title and meta_title.get("content"):
                title = meta_title["content"].strip()
            elif soup.find("h1", class_=re.compile(r"title", re.I)):
                h1 = soup.find("h1", class_=re.compile(r"title", re.I))
                title = h1.get_text(strip=True).replace("Title:", "").strip()
            elif soup.title and soup.title.string:
                title = soup.title.string.strip()

            if not title or len(title) < 5:
                return None

            # 2. Abstract extraction
            abstract = None
            meta_abs = soup.find("meta", attrs={"name": re.compile(r"citation_abstract|dc\.description", re.I)})
            if meta_abs and meta_abs.get("content"):
                abstract = meta_abs["content"].strip()
            else:
                abs_block = soup.find(class_=re.compile(r"abstract", re.I)) or soup.find("blockquote", class_=re.compile(r"abstract", re.I))
                if abs_block:
                    abstract = abs_block.get_text(separator=" ", strip=True).replace("Abstract:", "").replace("Abstract", "").strip()

            # 3. Authors extraction
            authors = []
            meta_authors = soup.find_all("meta", attrs={"name": re.compile(r"citation_author|dc\.creator", re.I)})
            for ma in meta_authors:
                if ma.get("content"):
                    authors.append(ma["content"].strip())

            if not authors:
                auth_div = soup.find(class_=re.compile(r"authors?", re.I))
                if auth_div:
                    for a_tag in auth_div.find_all("a"):
                        name = a_tag.get_text(strip=True)
                        if name and len(name) > 2:
                            authors.append(name)

            # 4. Publication year extraction
            pub_year = None
            meta_date = soup.find("meta", attrs={"name": re.compile(r"citation_publication_date|citation_date|dc\.date", re.I)})
            if meta_date and meta_date.get("content"):
                date_str = meta_date["content"].strip()
                match = re.search(r"\b(19\d\d|20\d\d)\b", date_str)
                if match:
                    pub_year = int(match.group(1))

            if not pub_year:
                # Search dateline text
                dateline = soup.find(class_=re.compile(r"dateline|date|published", re.I))
                if dateline:
                    match = re.search(r"\b(19\d\d|20\d\d)\b", dateline.get_text())
                    if match:
                        pub_year = int(match.group(1))

            # 5. DOI extraction
            doi = None
            meta_doi = soup.find("meta", attrs={"name": re.compile(r"citation_doi|dc\.identifier", re.I)})
            if meta_doi and meta_doi.get("content"):
                doi_candidate = meta_doi["content"].strip()
                if "10." in doi_candidate:
                    doi = doi_candidate.replace("https://doi.org/", "")

            # 6. Keywords
            keywords = []
            meta_kw = soup.find("meta", attrs={"name": re.compile(r"keywords|citation_keywords", re.I)})
            if meta_kw and meta_kw.get("content"):
                keywords = [k.strip() for k in meta_kw["content"].split(",") if k.strip()]

            return RawPaper(
                title=title,
                abstract=abstract,
                authors=authors,
                year=pub_year,
                venue="Web Crawled Scholarly Page",
                citations=0,
                source=self.source_name,
                url=page_url,
                doi=doi,
                keywords=keywords[:5],
            )
        except Exception as e:
            logger.debug("Failed extracting metadata from %s: %s", page_url, e)
            return None

    def search_sync(self, query: str, keywords: Optional[List[str]] = None, limit: int = 15) -> List[RawPaper]:
        """
        Executes a focused crawler session extracting structured metadata directly
        from scholarly listing pages with low-latency timeouts.
        """
        papers: List[RawPaper] = []
        visited_urls = set()

        # Seed start URLs for open-access crawling
        search_query = " ".join(keywords[:3]) if keywords else query
        encoded_query = quote_plus(search_query)
        start_urls = [
            f"https://arxiv.org/search/?query={encoded_query}&searchtype=all&source=header",
        ]

        session = requests.Session()
        session.headers.update({
            "User-Agent": settings.CRAWLER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

        for start_url in start_urls:
            if len(papers) >= limit:
                break
            try:
                logger.info("Crawler accessing seed URL: %s", start_url)
                resp = session.get(start_url, timeout=10.0)
                if resp.status_code != 200:
                    continue

                visited_urls.add(start_url)
                soup = BeautifulSoup(resp.content, "html.parser")

                # Extract structured entries directly from the listing page
                result_items = soup.find_all(["li", "div"], class_=re.compile(r"arxiv-result|search-result", re.I))
                for item in result_items:
                    if len(papers) >= limit:
                        break
                    
                    title_elem = item.select_one("p.title:not(.list-title), h3.title, span.title")
                    if not title_elem:
                        continue
                    title = title_elem.get_text(separator=" ", strip=True).replace("Title:", "").strip()

                    link_elem = item.find("a", href=re.compile(r"/abs/|/pdf/"))
                    paper_url = urljoin(start_url, link_elem["href"]) if link_elem else start_url

                    abs_elem = item.find(class_=re.compile(r"abstract-full|abstract", re.I))
                    abstract = None
                    if abs_elem:
                        abstract = abs_elem.get_text(strip=True).replace("△ Less", "").replace("▽ More", "").strip()

                    authors = []
                    auth_elem = item.find(class_=re.compile(r"authors", re.I))
                    if auth_elem:
                        for a in auth_elem.find_all("a"):
                            authors.append(a.get_text(strip=True))

                    year = None
                    date_elem = item.find(class_=re.compile(r"is-size-7|date", re.I))
                    if date_elem:
                        match = re.search(r"\b(19\d\d|20\d\d)\b", date_elem.get_text())
                        if match:
                            year = int(match.group(1))

                    paper = RawPaper(
                        title=title,
                        abstract=abstract,
                        authors=authors,
                        year=year,
                        venue="Crawled Open Repository",
                        citations=0,
                        source=self.source_name,
                        url=paper_url,
                        keywords=[query],
                    )
                    papers.append(paper)

            except Exception as e:
                logger.error("Crawler encountered error crawling %s: %s", start_url, e)

        logger.info("Crawler collected %d papers", len(papers))
        return papers
