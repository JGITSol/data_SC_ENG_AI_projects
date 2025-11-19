"""
Smart City Data Platform API

FastAPI server providing analytics endpoints for sensor data processed
by Spark Streaming and stored in PostgreSQL/S3.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os
import psycopg2
from psycopg2.extras import RealDictCursor

from src.storage import S3StorageManager

app = FastAPI(
    title="Smart City Data Platform API",
    description="Analytics API for smart city sensor data",
    version="2.0.0"
)


# Initialize storage manager
try:
    storage_manager = S3StorageManager()
except Exception as e:
    storage_manager = None
    print(f"Warning: S3 storage not available: {e}")


class SensorReading(BaseModel):
    """Sensor reading model."""
    sensor_id: str
    sensor_type: str
    city: str
    timestamp: datetime
    metrics: Dict[str, Any]


class AggregationResult(BaseModel):
    """Aggregation result model."""
    window_start: datetime
    window_end: datetime
    city: str
    district: str
    aggregation_type: str
    metrics: Dict[str, float]
    reading_count: int


def get_db_connection():
    """Get PostgreSQL database connection."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "smartcity"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres")
    )


@app.get("/health")
def health():
    """Health check endpoint."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check S3 status
    s3_status = "connected" if storage_manager else "not configured"
    if storage_manager:
        try:
            storage_manager.s3_client.head_bucket(Bucket=storage_manager.bucket_name)
        except Exception:
            s3_status = "error"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "storage": s3_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/ingest")
def ingest(reading: SensorReading):
    """
    Ingest sensor reading (stores to S3 for archival).
    
    Real-time data flows through Kafka → Spark → PostgreSQL.
    This endpoint is for backup/archival to S3.
    """
    if not storage_manager:
        raise HTTPException(status_code=503, detail="Storage not available")
    
    try:
        reading_dict = reading.dict()
        reading_dict["timestamp"] = reading.timestamp.isoformat()
        
        key = storage_manager.upload_sensor_reading(reading_dict)
        
        return {
            "status": "stored",
            "s3_key": key,
            "sensor_id": reading.sensor_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/query/air-quality")
def query_air_quality(
    city: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(100, le=1000)
):
    """Query air quality aggregations."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = """
            SELECT 
                window_start, window_end, city, district,
                avg_pm25, max_pm25, avg_pm10, max_pm10,
                avg_no2, avg_co2, reading_count, processing_time
            FROM air_quality_agg
            WHERE window_start >= %s
        """
        params = [cutoff_time]
        
        if city:
            query += " AND city = %s"
            params.append(city)
        
        query += " ORDER BY window_start DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "aggregation_type": "air_quality",
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/query/traffic")
def query_traffic(
    city: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(100, le=1000)
):
    """Query traffic aggregations."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = """
            SELECT 
                window_start, window_end, city, district,
                avg_vehicle_count, avg_speed, avg_congestion,
                reading_count, processing_time
            FROM traffic_agg
            WHERE window_start >= %s
        """
        params = [cutoff_time]
        
        if city:
            query += " AND city = %s" 
            params.append(city)
        
        query += " ORDER BY window_start DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "aggregation_type": "traffic",
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/query/energy")
def query_energy(
    city: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(100, le=1000)
):
    """Query energy consumption aggregations."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = """
            SELECT 
                window_start, window_end, city, district,
                avg_power_consumption, max_power_consumption,
                avg_voltage, avg_current, reading_count, processing_time
            FROM energy_agg
            WHERE window_start >= %s
        """
        params = [cutoff_time]
        
        if city:
            query += " AND city = %s"
            params.append(city)
        
        query += " ORDER BY window_start DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "aggregation_type": "energy",
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/storage/stats")
def storage_stats():
    """Get S3 storage statistics."""
    if not storage_manager:
        raise HTTPException(status_code=503, detail="Storage not available")
    
    try:
        stats = storage_manager.get_bucket_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/storage/list")
def list_stored_data(
    prefix: str = Query("", description="S3 key prefix filter"),
    limit: int = Query(100, le=1000)
):
    """List stored data in S3."""
    if not storage_manager:
        raise HTTPException(status_code=503, detail="Storage not available")
    
    try:
        objects = storage_manager.list_objects(prefix=prefix, max_keys=limit)
        return {
            "count": len(objects),
            "objects": objects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

