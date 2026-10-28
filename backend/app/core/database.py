from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings
from app.core.logging import logger

connect_args = {}
db_url = settings.DATABASE_URL

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# Support PostgreSQL primary with graceful local dev fallback if local PostgreSQL server is offline
try:
    if db_url.startswith("postgresql"):
        # Test connection briefly
        test_engine = create_engine(db_url, connect_args={"connect_timeout": 2})
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine = test_engine
        logger.info(f"Connected to primary PostgreSQL database at {db_url.split('@')[-1] if '@' in db_url else 'local'}")
    else:
        engine = create_engine(db_url, connect_args=connect_args)
except Exception as e:
    if settings.ENVIRONMENT in ("development", "test"):
        dev_db_url = "sqlite:///./devguard_dev.db"
        logger.warning(
            f"Primary PostgreSQL server unreachable ({e}). "
            f"Falling back to local development database '{dev_db_url}'. "
            f"For production, ensure PostgreSQL is running."
        )
        engine = create_engine(dev_db_url, connect_args={"check_same_thread": False})
    else:
        logger.error(f"Failed to connect to required PostgreSQL database: {e}")
        raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a database session with automatic commit / rollback.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session rolled back due to error: {e}")
        raise
    finally:
        db.close()
