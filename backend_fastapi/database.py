import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Supports PostgreSQL, MySQL, and zero-config local SQLite fallback on Windows:
# PostgreSQL: set DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce_db
# MySQL:      set DATABASE_URL=mysql+pymysql://user:password@localhost:3306/ecommerce_db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ecommerce_db.sqlite3")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
