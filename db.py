# DB bootstrap & models — Postgres if DATABASE_URL set; else SQLite
import os
from datetime import date, datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Date, DateTime, Float, JSON, ForeignKey
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.pool import NullPool

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=3, max_overflow=5)
else:
    os.makedirs("data", exist_ok=True)
    engine = create_engine("sqlite:///data/crooks.db", poolclass=NullPool)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    rel_path = Column(String(512), nullable=False)
    bytes = Column(Integer, default=0)
    type = Column(String(32))
    thumbnail = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)

    def as_dict(self):
        return {
            "id": self.id, "filename": self.filename, "path": self.rel_path,
            "size_bytes": self.bytes, "type": self.type, "thumbnail": self.thumbnail,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    budget_allocation = Column(Float, default=0.0)
    deliverables = Column(JSON, default=[])
    assets_mapped = Column(JSON, default=[])
    cultural_context = Column(Text, default="")
    target_kpis = Column(JSON, default={})
    status = Column(String(64), default="planned")

class Agency(Base):
    __tablename__ = "agencies"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    phase = Column(Integer, default=1)
    monthly_budget = Column(Float, default=0.0)
    budget_used = Column(Float, default=0.0)
    on_time_delivery = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    current_deliverables = Column(Integer, default=0)
    response_time = Column(String(64), default="")
    revision_rounds = Column(String(64), default="")
    client_satisfaction = Column(String(64), default="")
    projects = relationship("AgencyProject", back_populates="agency", cascade="all, delete-orphan")

class AgencyProject(Base):
    __tablename__ = "agency_projects"
    id = Column(Integer, primary_key=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"))
    name = Column(String(255), nullable=False)
    status = Column(String(64), default="pending")
    due_date = Column(Date)
    agency = relationship("Agency", back_populates="projects")

def init_db():
    Base.metadata.create_all(bind=engine)
