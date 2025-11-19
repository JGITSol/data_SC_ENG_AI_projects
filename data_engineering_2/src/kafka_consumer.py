"""
Kafka consumer for urban mobility data streaming.

Consumes events from Kafka, processes them, and stores in PostgreSQL.
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from kafka import KafkaConsumer
from kafka.errors import KafkaError
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MobilityEventProcessor:
    """Process and validate mobility events."""
    
    @staticmethod
    def validate_event(event: Dict[str, Any]) -> bool:
        """
        Validate event structure and data quality.
        
        Args:
            event: Event dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            "trip_id", "city", "vehicle_type", "start_location",
            "end_location", "distance_km", "duration_minutes", "cost", "timestamp"
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in event:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate data ranges
        if event["distance_km"] < 0 or event["distance_km"] > 100:
            logger.warning(f"Invalid distance: {event['distance_km']}")
            return False
        
        if event["duration_minutes"] < 0 or event["duration_minutes"] > 300:
            logger.warning(f"Invalid duration: {event['duration_minutes']}")
            return False
        
        if event["cost"] < 0 or event["cost"] > 1000:
            logger.warning(f"Invalid cost: {event['cost']}")
            return False
        
        return True
    
    @staticmethod
    def enrich_event(event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich event with calculated fields.
        
        Args:
            event: Original event
            
        Returns:
            Enriched event
        """
        # Calculate average speed
        if event["duration_minutes"] > 0:
            event["avg_speed_kmh"] = round(
                (event["distance_km"] / event["duration_minutes"]) * 60, 2
            )
        else:
            event["avg_speed_kmh"] = 0.0
        
        # Calculate cost per km
        if event["distance_km"] > 0:
            event["cost_per_km"] = round(event["cost"] / event["distance_km"], 2)
        else:
            event["cost_per_km"] = 0.0
        
        # Add processing timestamp
        event["processed_at"] = datetime.utcnow().isoformat()
        
        return event


class PostgreSQLWriter:
    """Write events to PostgreSQL database."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "mobility",
        user: str = "postgres",
        password: str = "postgres"
    ):
        """
        Initialize PostgreSQL connection.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
        """
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        self.conn.autocommit = False
        logger.info(f"Connected to PostgreSQL: {database}@{host}:{port}")
        
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create tables if they don't exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS mobility_events (
            id SERIAL PRIMARY KEY,
            trip_id VARCHAR(50) UNIQUE NOT NULL,
            city VARCHAR(50) NOT NULL,
            district VARCHAR(50),
            vehicle_type VARCHAR(20) NOT NULL,
            start_lat DECIMAL(10, 6),
            start_lon DECIMAL(10, 6),
            end_lat DECIMAL(10, 6),
            end_lon DECIMAL(10, 6),
            distance_km DECIMAL(10, 2),
            duration_minutes DECIMAL(10, 2),
            cost DECIMAL(10, 2),
            avg_speed_kmh DECIMAL(10, 2),
            cost_per_km DECIMAL(10, 2),
            timestamp TIMESTAMP,
            processed_at TIMESTAMP,
            weather VARCHAR(20),
            temperature_c DECIMAL(5, 1),
            is_weekend BOOLEAN,
            hour_of_day INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_city ON mobility_events(city);
        CREATE INDEX IF NOT EXISTS idx_vehicle_type ON mobility_events(vehicle_type);
        CREATE INDEX IF NOT EXISTS idx_timestamp ON mobility_events(timestamp);
        """
        
        with self.conn.cursor() as cursor:
            cursor.execute(create_table_sql)
            self.conn.commit()
        
        logger.info("Database schema ensured")
    
    def write_event(self, event: Dict[str, Any]) -> bool:
        """
        Write a single event to database.
        
        Args:
            event: Event dictionary
            
        Returns:
            True if successful, False otherwise
        """
        insert_sql = """
        INSERT INTO mobility_events (
            trip_id, city, district, vehicle_type,
            start_lat, start_lon, end_lat, end_lon,
            distance_km, duration_minutes, cost,
            avg_speed_kmh, cost_per_km, timestamp, processed_at,
            weather, temperature_c, is_weekend, hour_of_day
        ) VALUES (
            %(trip_id)s, %(city)s, %(district)s, %(vehicle_type)s,
            %(start_lat)s, %(start_lon)s, %(end_lat)s, %(end_lon)s,
            %(distance_km)s, %(duration_minutes)s, %(cost)s,
            %(avg_speed_kmh)s, %(cost_per_km)s, %(timestamp)s, %(processed_at)s,
            %(weather)s, %(temperature_c)s, %(is_weekend)s, %(hour_of_day)s
        )
        ON CONFLICT (trip_id) DO NOTHING
        """
        
        try:
            data = {
                "trip_id": event["trip_id"],
                "city": event["city"],
                "district": event.get("district"),
                "vehicle_type": event["vehicle_type"],
                "start_lat": event["start_location"]["lat"],
                "start_lon": event["start_location"]["lon"],
                "end_lat": event["end_location"]["lat"],
                "end_lon": event["end_location"]["lon"],
                "distance_km": event["distance_km"],
                "duration_minutes": event["duration_minutes"],
                "cost": event["cost"],
                "avg_speed_kmh": event.get("avg_speed_kmh", 0.0),
                "cost_per_km": event.get("cost_per_km", 0.0),
                "timestamp": event["timestamp"],
                "processed_at": event.get("processed_at"),
                "weather": event.get("metadata", {}).get("weather"),
                "temperature_c": event.get("metadata", {}).get("temperature_c"),
                "is_weekend": event.get("metadata", {}).get("is_weekend"),
                "hour_of_day": event.get("metadata", {}).get("hour_of_day")
            }
            
            with self.conn.cursor() as cursor:
                cursor.execute(insert_sql, data)
                self.conn.commit()
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to write event: {e}")
            self.conn.rollback()
            return False
    
    def close(self):
        """Close database connection."""
        self.conn.close()
        logger.info("Database connection closed")


class MobilityKafkaConsumer:
    """Kafka consumer for urban mobility events."""
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "urban-mobility-events",
        group_id: str = "mobility-consumer-group",
        db_config: Dict[str, Any] = None
    ):
        """
        Initialize Kafka consumer.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
            topic: Kafka topic to consume from
            group_id: Consumer group ID
            db_config: Database configuration
        """
        self.topic = topic
        self.processor = MobilityEventProcessor()
        
        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        
        logger.info(f"Kafka consumer initialized for topic: {topic}")
        
        # Initialize database writer
        db_config = db_config or {}
        self.db_writer = PostgreSQLWriter(**db_config)
        
        self.events_processed = 0
        self.events_failed = 0
    
    def consume(self):
        """Start consuming messages from Kafka."""
        logger.info("Starting consumer...")
        
        try:
            for message in self.consumer:
                try:
                    event = message.value
                    
                    # Validate event
                    if not self.processor.validate_event(event):
                        self.events_failed += 1
                        continue
                    
                    # Enrich event
                    enriched_event = self.processor.enrich_event(event)
                    
                    # Write to database
                    if self.db_writer.write_event(enriched_event):
                        self.events_processed += 1
                    else:
                        self.events_failed += 1
                    
                    # Log progress
                    if self.events_processed % 100 == 0:
                        logger.info(
                            f"Processed: {self.events_processed}, "
                            f"Failed: {self.events_failed}"
                        )
                
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    self.events_failed += 1
        
        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
        
        finally:
            self.close()
        
        logger.info(
            f"Final stats - Processed: {self.events_processed}, "
            f"Failed: {self.events_failed}"
        )
    
    def close(self):
        """Close consumer and database connection."""
        logger.info("Closing consumer...")
        self.consumer.close()
        self.db_writer.close()


def main():
    """Main entry point for standalone execution."""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="Urban Mobility Kafka Consumer")
    parser.add_argument(
        "--bootstrap-servers",
        default=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        help="Kafka bootstrap servers"
    )
    parser.add_argument(
        "--topic",
        default="urban-mobility-events",
        help="Kafka topic"
    )
    parser.add_argument(
        "--group-id",
        default="mobility-consumer-group",
        help="Consumer group ID"
    )
    
    args = parser.parse_args()
    
    db_config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "database": os.getenv("DB_NAME", "mobility"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres")
    }
    
    consumer = MobilityKafkaConsumer(
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic,
        group_id=args.group_id,
        db_config=db_config
    )
    
    consumer.consume()


if __name__ == "__main__":
    main()
