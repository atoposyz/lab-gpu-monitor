from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings

engine = create_engine(
    settings.sqlalchemy_database_uri,
    future=True,
    echo=(settings.app_env == "dev"),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
