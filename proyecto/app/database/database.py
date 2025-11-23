from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# Locate proyecto/ as BASE_DIR (this file is proyecto/app/database/database.py)
BASE_DIR = Path(__file__).resolve().parents[2]

# Try to import Base from proyecto.modelo.seguridad (with fallback)
try:
    from proyecto.modelo.seguridad import Base
except Exception:
    from modelo.seguridad import Base

DATABASE_URL = f"sqlite:///{BASE_DIR / 'data.db'}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency generator for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create DB tables if not present"""
    Base.metadata.create_all(bind=engine)


# initialize on import so tables exist
init_db()