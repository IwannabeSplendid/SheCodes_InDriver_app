import os
from supabase import create_client, Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator


from .settings import get_settings


settings = get_settings()

# Supabase db
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Local db
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=0,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_local_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_supabase_db():
    return supabase
