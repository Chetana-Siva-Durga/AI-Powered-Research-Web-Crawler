import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load .env file from project root or backend directory
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = "Research Scope"
    PROJECT_DESCRIPTION: str = "AI-Based Scholarly Research Analysis Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Database settings (MySQL primary, SQLite fallback)
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "research_scope")
    
    MYSQL_URL: str = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    )
    SQLITE_FALLBACK_URL: str = "sqlite:///./research_scope.db"
    
    # Force SQLite if set to True
    USE_SQLITE_FORCE: bool = os.getenv("USE_SQLITE_FORCE", "False").lower() in ("true", "1", "yes")

    # CORS origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ]

    # Scholarly API Keys (optional; polite/public pools work without them)
    SEMANTIC_SCHOLAR_API_KEY: str = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
    OPENALEX_API_KEY: str = os.getenv("OPENALEX_API_KEY", "")
    CROSSREF_MAILTO: str = os.getenv("CROSSREF_MAILTO", "researcher@example.com")
    PUBMED_API_KEY: str = os.getenv("PUBMED_API_KEY", "")
    
    # Optional LLM API keys for enhanced natural language explanation
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Crawler Settings
    CRAWLER_ENABLED: bool = True
    CRAWLER_MAX_RESULTS: int = int(os.getenv("CRAWLER_MAX_RESULTS", "25"))
    CRAWLER_USER_AGENT: str = "ResearchScopeCrawler/1.0 (Scholarly Research Harvester; ethical academic bot)"


settings = Settings()
