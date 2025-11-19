"""
Kafka producer for urban mobility data streaming.

Generates realistic urban mobility events (bike shares, scooters, buses, etc.)
and publishes them to Kafka topics.
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from kafka import KafkaProducer
from kafka.errors import KafkaError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UrbanMobilityDataGenerator:
    """Generate realistic urban mobility events."""
    
    CITIES = ["Warsaw", "Krakow", "Gdansk", "Wroclaw", "Poznan"]
    VEHICLE_TYPES = ["bike", "scooter", "bus", "tram", "metro"]
    DISTRICTS = [
        "Srodmiescie", "Mokotow", "Praga", "Wola", "Zoliborz",
        "Ochota", "Ursynow", "Bielany", "Targowek", "Bemowo"
    ]
    
    def __init__(self):
        """Initialize the data generator."""
        self.trip_id_counter = 0
    
    def generate_trip_event(self) -> Dict[str, Any]:
        """Generate a single trip event."""
        self.trip_id_counter += 1
        
        city = random.choice(self.CITIES)
        vehicle_type = random.choice(self.VEHICLE_TYPES)
        district = random.choice(self.DISTRICTS)
        
        # Generate coordinates (roughly Warsaw area)
        base_lat = 52.2297
        base_lon = 21.0122
        start_lat = base_lat + random.uniform(-0.1, 0.1)
        start_lon = base_lon + random.uniform(-0.1, 0.1)
        end_lat = base_lat + random.uniform(-0.1, 0.1)
        end_lon = base_lon + random.uniform(-0.1, 0.1)
        
        # Calculate distance (simplified)
        distance_km = random.uniform(0.5, 15.0)
        
        # Generate duration based on vehicle type
        if vehicle_type in ["bike", "scooter"]:
            duration_minutes = random.uniform(5, 45)
        elif vehicle_type in ["bus", "tram"]:
            duration_minutes = random.uniform(10, 60)
        else:  # metro
            duration_minutes = random.uniform(5, 30)
        
        # Generate cost
        if vehicle_type in ["bike", "scooter"]:
            cost = round(random.uniform(3.0, 25.0), 2)
        else:  # public transport
            cost = round(random.uniform(3.0, 7.0), 2)
        
        # Generate timestamp
        timestamp = datetime.utcnow()
        
        event = {
            "trip_id": f"TRIP-{self.trip_id_counter:08d}",
            "city": city,
            "district": district,
            "vehicle_type": vehicle_type,
            "start_location": {
                "lat": round(start_lat, 6),
                "lon": round(start_lon, 6)
            },
            "end_location": {
                "lat": round(end_lat, 6),
                "lon": round(end_lon, 6)
            },
            "distance_km": round(distance_km, 2),
            "duration_minutes": round(duration_minutes, 2),
            "cost": cost,
            "timestamp": timestamp.isoformat(),
            "metadata": {
                "weather": random.choice(["sunny", "cloudy", "rainy", "snowy"]),
                "temperature_c": round(random.uniform(-10, 30), 1),
                "is_weekend": timestamp.weekday() >= 5,
                "hour_of_day": timestamp.hour
            }
        }
        
        return event


class MobilityKafkaProducer:
    """Kafka producer for urban mobility data."""
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "urban-mobility-events"
    ):
        """
        Initialize Kafka producer.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
            topic: Kafka topic to publish to
        """
        self.topic = topic
        self.generator = UrbanMobilityDataGenerator()
        
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            logger.info(f"Kafka producer initialized for topic: {self.topic}")
        except KafkaError as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise
    
    def send_event(self, event: Dict[str, Any]) -> None:
        """
        Send a single event to Kafka.
        
        Args:
            event: Event dictionary to send
        """
        try:
            # Use city as partition key for better distribution
            key = event['city']
            future = self.producer.send(self.topic, key=key, value=event)
            
            # Wait for send to complete (with timeout)
            record_metadata = future.get(timeout=10)
            logger.debug(
                f"Sent event {event['trip_id']} to partition {record_metadata.partition} "
                f"at offset {record_metadata.offset}"
            )
        except KafkaError as e:
            logger.error(f"Failed to send event: {e}")
            raise
    
    def produce_continuous(self, events_per_second: float = 10.0, duration_seconds: int = None):
        """
        Continuously produce events at specified rate.
        
        Args:
            events_per_second: Rate of event generation
            duration_seconds: How long to run (None = infinite)
        """
        logger.info(f"Starting continuous production at {events_per_second} events/sec")
        
        interval = 1.0 / events_per_second
        start_time = time.time()
        events_sent = 0
        
        try:
            while True:
                event = self.generator.generate_trip_event()
                self.send_event(event)
                events_sent += 1
                
                if events_sent % 100 == 0:
                    logger.info(f"Sent {events_sent} events")
                
                # Check duration limit
                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    break
                
                # Sleep to maintain rate
                time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("Producer stopped by user")
        finally:
            self.close()
        
        elapsed = time.time() - start_time
        logger.info(f"Sent {events_sent} events in {elapsed:.2f} seconds "
                   f"({events_sent/elapsed:.2f} events/sec)")
    
    def close(self):
        """Close the producer and flush pending messages."""
        logger.info("Flushing and closing producer...")
        self.producer.flush()
        self.producer.close()


def main():
    """Main entry point for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Urban Mobility Kafka Producer")
    parser.add_argument(
        "--bootstrap-servers",
        default="localhost:9092",
        help="Kafka bootstrap servers"
    )
    parser.add_argument(
        "--topic",
        default="urban-mobility-events",
        help="Kafka topic"
    )
    parser.add_argument(
        "--rate",
        type=float,
        default=10.0,
        help="Events per second"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=None,
        help="Duration in seconds (default: infinite)"
    )
    
    args = parser.parse_args()
    
    producer = MobilityKafkaProducer(
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic
    )
    
    producer.produce_continuous(
        events_per_second=args.rate,
        duration_seconds=args.duration
    )


if __name__ == "__main__":
    main()
