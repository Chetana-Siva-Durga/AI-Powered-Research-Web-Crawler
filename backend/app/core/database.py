import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

logger = logging.getLogger("research_scope.database")
logging.basicConfig(level=logging.INFO)

Base = declarative_base()

def get_engine():
    """
    Attempts to create a connection engine to MySQL.
    Falls back gracefully to SQLite if MySQL is unreachable or disabled.
    """
    if not settings.USE_SQLITE_FORCE:
        try:
            logger.info("Attempting connection to MySQL: %s:%s/%s", 
                        settings.MYSQL_HOST, settings.MYSQL_PORT, settings.MYSQL_DB)
            mysql_engine = create_engine(
                settings.MYSQL_URL,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={"connect_timeout": 3}
            )
            # Test connection
            with mysql_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to MySQL database: %s", settings.MYSQL_DB)
            return mysql_engine
        except Exception as e:
            logger.warning(
                "MySQL connection could not be established (%s). Falling back to SQLite.", e
            )
    
    # SQLite fallback
    logger.info("Using SQLite database at %s", settings.SQLITE_FALLBACK_URL)
    sqlite_engine = create_engine(
        settings.SQLITE_FALLBACK_URL,
        connect_args={"check_same_thread": False}
    )
    return sqlite_engine


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency to yield a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initializes all database tables registered on Base."""
    # Import models here so they are registered with Base metadata
    import app.models.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created successfully.")
