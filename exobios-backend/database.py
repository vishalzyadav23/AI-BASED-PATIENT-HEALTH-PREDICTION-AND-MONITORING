# backend/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Grab the URL from Render's environment, or fallback to local SQLite for your presentation
db_url = os.getenv("DATABASE_URL", "sqlite:///./exobios_local.db")

# CRITICAL RENDER FIX: Render supplies URLs starting with 'postgres://'
# Modern SQLAlchemy strictly requires 'postgresql://'. This line fixes it automatically.
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URL = db_url

# For SQLite (local testing), we MUST pass check_same_thread=False to prevent FastAPI crashes
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # For PostgreSQL (Render production)
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()