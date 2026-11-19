import re
import scrapy


class ScholarlyResearchSpider(scrapy.Spider):
    name = "scholarly_spider"
    allowed_domains = ["arxiv.org", "aclweb.org", "biorxiv.org"]

    def __init__(self, query="machine learning", max_pages=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query = query
        self.max_pages = int(max_pages)
        self.start_urls = [
            f"https://arxiv.org/search/?query={scrapy.utils.python.to_unicode(query)}&searchtype=all"
        ]

    def parse(self, response):
        """Parse search listing and extract paper details or follow links."""
        # Extract arXiv search result entries
        results = response.css("li.arxiv-result")
        for item in results:
            title = item.css("p.title::text").get()
            if not title:
                title = item.css("p.title span::text").get()
            if title:
                title = title.replace("Title:", "").strip()

            authors = item.css("p.authors a::text").getall()
            abstract = item.css("span.abstract-full::text").get()
            if not abstract:
                abstract = item.css("span.abstract-short::text").get()

            date_str = item.css("p.is-size-7::text").get()
            year = None
            if date_str:
                match = re.search(r"\b(19\d\d|20\d\d)\b", date_str)
                if match:
                    year = int(match.group(1))

            link = item.css("p.list-title a::attr(href)").get()

            yield {
                "title": title,
                "abstract": abstract.strip() if abstract else None,
                "authors": authors,
                "year": year,
                "source": "crawler_scrapy",
                "url": response.urljoin(link) if link else response.url,
            }

        # Follow pagination if available
        next_page = response.css("a.pagination-next::attr(href)").get()
        if next_page and self.max_pages > 1:
            self.max_pages -= 1
            yield response.follow(next_page, self.parse)
