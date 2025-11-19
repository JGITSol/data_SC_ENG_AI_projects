"""
Database models and utilities for urban mobility data.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class MobilityEvent(Base):
    """Model for mobility events."""
    
    __tablename__ = "mobility_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(String(50), unique=True, nullable=False, index=True)
    city = Column(String(50), nullable=False, index=True)
    district = Column(String(50))
    vehicle_type = Column(String(20), nullable=False, index=True)
    start_lat = Column(DECIMAL(10, 6))
    start_lon = Column(DECIMAL(10, 6))
    end_lat = Column(DECIMAL(10, 6))
    end_lon = Column(DECIMAL(10, 6))
    distance_km = Column(DECIMAL(10, 2))
    duration_minutes = Column(DECIMAL(10, 2))
    cost = Column(DECIMAL(10, 2))
    avg_speed_kmh = Column(DECIMAL(10, 2))
    cost_per_km = Column(DECIMAL(10, 2))
    timestamp = Column(DateTime, index=True)
    processed_at = Column(DateTime)
    weather = Column(String(20))
    temperature_c = Column(DECIMAL(5, 1))
    is_weekend = Column(Boolean)
    hour_of_day = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MobilityEvent {self.trip_id} - {self.city} - {self.vehicle_type}>"


def get_database_url() -> str:
    """Get database URL from environment or use defaults."""
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "mobility")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def create_tables():
    """Create all database tables."""
    engine = create_engine(get_database_url())
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get database session."""
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    return Session()
