import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
 
load_dotenv()
 
DATABASE_URL = os.getenv("DATABASE_URL")
 
# Neon suspends connections after ~5 min idle — keepalives don't help because
# Neon kills the SSL session server-side before they fire.
# NullPool = never hold a connection open between requests; get a fresh one
# each time. Slightly slower per-request but eliminates all SSL drop errors.
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={
        "sslmode":            "require",
        "connect_timeout":    10,
        "application_name":   "mykepatuhan",
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