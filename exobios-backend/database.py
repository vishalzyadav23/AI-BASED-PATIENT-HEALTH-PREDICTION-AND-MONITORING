# backend/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Grab the URL from Render's environment, or fallback to local
db_url = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/exobios")

# CRITICAL RENDER FIX: Render supplies URLs starting with 'postgres://'
# Modern SQLAlchemy strictly requires 'postgresql://'. This line fixes it automatically.
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URL = db_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()