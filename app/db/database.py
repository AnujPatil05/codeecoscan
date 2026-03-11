"""SQLite database setup for CodeEcoScan.

Uses SQLAlchemy 2.x with async support.
Database file: codeecoscan.db (in the project root, or $DATA_DIR env var).
"""

from __future__ import annotations

import os
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# ── Database path ────────────────────────────────────────────────────

_DATA_DIR = os.environ.get("DATA_DIR", ".")
DB_PATH = os.path.join(_DATA_DIR, "codeecoscan.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# ── ORM models ──────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


class AnalysisRun(Base):
    """Stores each code analysis result."""
    __tablename__ = "analysis_runs"

    id              = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False)
    source          = Column(String(32), default="paste", nullable=False)  # paste | file | repo
    filename        = Column(String(256), nullable=True)
    code_hash       = Column(String(64), nullable=True, index=True)
    score           = Column(Integer, nullable=False)
    risk_level      = Column(String(16), nullable=False)
    loop_score      = Column(Integer, default=0)
    interaction     = Column(Integer, default=0)
    recursion       = Column(Integer, default=0)
    heavy_imports   = Column(Integer, default=0)
    issue_count     = Column(Integer, default=0)
    co2_kg_per_day  = Column(Float, default=0.0)


class RepoScan(Base):
    """Stores repository scan results."""
    __tablename__ = "repo_scans"

    id              = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False)
    repo_url        = Column(String(512), nullable=False)
    repo_name       = Column(String(256), nullable=False)
    files_analyzed  = Column(Integer, default=0)
    repo_score      = Column(Integer, default=0)
    top_files_json  = Column(Text, nullable=True)   # JSON array
    alerts_json     = Column(Text, nullable=True)    # JSON array


# ── Database init ────────────────────────────────────────────────────

def init_db() -> None:
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """FastAPI dependency: yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
