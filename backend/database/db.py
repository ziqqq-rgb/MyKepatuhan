from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool

from core import config

engine = create_engine(
    config.DATABASE_URL,       # use the "-pooler" host from Neon dashboard
    poolclass=QueuePool,
    pool_size=3,
    max_overflow=2,
    pool_pre_ping=True,        # discard dead connections instead of erroring
    pool_recycle=280,          # recycle before Neon's ~5min idle cutoff
    connect_args={
        "sslmode":          "require",
        "connect_timeout":  10,
        "application_name": "mykepatuhan",
    },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()