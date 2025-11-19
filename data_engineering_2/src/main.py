"""
Urban Mobility Analytics API

FastAPI server providing analytics and monitoring endpoints for the
real-time urban mobility data pipeline.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os

from src.database import get_session, MobilityEvent
from sqlalchemy import func, desc

app = FastAPI(
    title="Urban Mobility Analytics API",
    description="Real-time analytics for urban mobility data",
    version="1.0.0"
)


class AnalyticsResponse(BaseModel):
    """Analytics query response."""
    total_trips: int
    total_distance_km: float
    total_revenue: float
    avg_trip_distance: float
    avg_trip_duration: float
    avg_cost: float
    breakdown_by_vehicle: Dict[str, int]
    breakdown_by_city: Dict[str, int]


class TripEvent(BaseModel):
    """Single trip event."""
    trip_id: str
    city: str
    vehicle_type: str
    distance_km: float
    duration_minutes: float
    cost: float
    timestamp: datetime


@app.get("/health")
def health():
    """Health check endpoint."""
    try:
        session = get_session()
        count = session.query(MobilityEvent).count()
        session.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_events": count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@app.get("/api/analytics", response_model=AnalyticsResponse)
def get_analytics(
    hours: int = Query(24, description="Time window in hours"),
    city: Optional[str] = Query(None, description="Filter by city"),
    vehicle_type: Optional[str] = Query(None, description="Filter by vehicle type")
):
    """
    Get analytics for mobility events.
    
    Args:
        hours: Time window in hours (default: 24)
        city: Optional city filter
        vehicle_type: Optional vehicle type filter
    
    Returns:
        Analytics summary
    """
    try:
        session = get_session()
        
        # Build query with time filter
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        query = session.query(MobilityEvent).filter(
            MobilityEvent.timestamp >= cutoff_time
        )
        
        # Apply optional filters
        if city:
            query = query.filter(MobilityEvent.city == city)
        if vehicle_type:
            query = query.filter(MobilityEvent.vehicle_type == vehicle_type)
        
        # Get all events
        events = query.all()
        
        if not events:
            raise HTTPException(status_code=404, detail="No events found")
        
        # Calculate aggregates
        total_trips = len(events)
        total_distance = sum(float(e.distance_km or 0) for e in events)
        total_revenue = sum(float(e.cost or 0) for e in events)
        avg_distance = total_distance / total_trips if total_trips > 0 else 0
        avg_duration = sum(float(e.duration_minutes or 0) for e in events) / total_trips if total_trips > 0 else 0
        avg_cost = total_revenue / total_trips if total_trips > 0 else 0
        
        # Breakdown by vehicle type
        vehicle_breakdown = {}
        for event in events:
            vtype = event.vehicle_type
            vehicle_breakdown[vtype] = vehicle_breakdown.get(vtype, 0) + 1
        
        # Breakdown by city
        city_breakdown = {}
        for event in events:
            c = event.city
            city_breakdown[c] = city_breakdown.get(c, 0) + 1
        
        session.close()
        
        return AnalyticsResponse(
            total_trips=total_trips,
            total_distance_km=round(total_distance, 2),
            total_revenue=round(total_revenue, 2),
            avg_trip_distance=round(avg_distance, 2),
            avg_trip_duration=round(avg_duration, 2),
            avg_cost=round(avg_cost, 2),
            breakdown_by_vehicle=vehicle_breakdown,
            breakdown_by_city=city_breakdown
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recent-trips", response_model=List[TripEvent])
def get_recent_trips(
    limit: int = Query(100, description="Number of trips to return", le=1000),
    city: Optional[str] = Query(None, description="Filter by city"),
    vehicle_type: Optional[str] = Query(None, description="Filter by vehicle type")
):
    """
    Get recent trip events.
    
    Args:
        limit: Maximum number of trips to return
        city: Optional city filter
        vehicle_type: Optional vehicle type filter
    
    Returns:
        List of recent trips
    """
    try:
        session = get_session()
        
        query = session.query(MobilityEvent).order_by(desc(MobilityEvent.timestamp))
        
        if city:
            query = query.filter(MobilityEvent.city == city)
        if vehicle_type:
            query = query.filter(MobilityEvent.vehicle_type == vehicle_type)
        
        events = query.limit(limit).all()
        
        session.close()
        
        return [
            TripEvent(
                trip_id=e.trip_id,
                city=e.city,
                vehicle_type=e.vehicle_type,
                distance_km=float(e.distance_km or 0),
                duration_minutes=float(e.duration_minutes or 0),
                cost=float(e.cost or 0),
                timestamp=e.timestamp
            )
            for e in events
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
def get_stats():
    """Get overall system statistics."""
    try:
        session = get_session()
        
        total_events = session.query(MobilityEvent).count()
        
        # Get date range
        first_event = session.query(func.min(MobilityEvent.timestamp)).scalar()
        last_event = session.query(func.max(MobilityEvent.timestamp)).scalar()
        
        # Get unique cities and vehicle types
        cities = session.query(MobilityEvent.city).distinct().count()
        vehicle_types = session.query(MobilityEvent.vehicle_type).distinct().count()
        
        session.close()
        
        return {
            "total_events": total_events,
            "first_event": first_event.isoformat() if first_event else None,
            "last_event": last_event.isoformat() if last_event else None,
            "unique_cities": cities,
            "unique_vehicle_types": vehicle_types,
            "database_connected": True
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"error": str(e), "database_connected": False}
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

