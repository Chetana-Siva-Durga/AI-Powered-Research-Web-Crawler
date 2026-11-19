# Scrapy settings for Research Scope crawler
BOT_NAME = "research_scope_crawler"

SPIDER_MODULES = ["app.crawler_service.spiders"]
NEWSPIDER_MODULE = "app.crawler_service.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Polite concurrency and rate limiting
CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = 1.0

# User agent header
USER_AGENT = "ResearchScopeCrawler/1.0 (Scholarly Harvester; +http://researchscope.org)"

# Disable cookies (not needed for scholarly scraping)
COOKIES_ENABLED = False

# AutoThrottle extension to dynamically adjust delay
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Request header defaults
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
}
