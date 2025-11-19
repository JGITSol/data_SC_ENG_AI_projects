"""
Smart City Sensor Data Simulator

Generates realistic IoT sensor data for smart city applications:
- Air quality sensors
- Traffic sensors
- Parking sensors
- Weather stations
- Energy meters
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


class SensorDataGenerator:
    """Generate realistic smart city sensor data."""
    
    CITIES = ["Warsaw", "Krakow", "Gdansk", "Wroclaw", "Poznan"]
    DISTRICTS = [
        "Srodmiescie", "Mokotow", "Praga", "Wola", "Zoliborz",
        "Ochota", "Ursynow", "Bielany", "Targowek", "Bemowo"
    ]
    
    SENSOR_TYPES = {
        "air_quality": {
            "metrics": ["pm25", "pm10", "no2", "co2", "temperature", "humidity"],
            "units": {"pm25": "μg/m³", "pm10": "μg/m³", "no2": "ppb", "co2": "ppm", "temperature": "°C", "humidity": "%"}
        },
        "traffic": {
            "metrics": ["vehicle_count", "average_speed", "congestion_level"],
            "units": {"vehicle_count": "vehicles/hour", "average_speed": "km/h", "congestion_level": "0-10"}
        },
        "parking": {
            "metrics": ["occupied_spots", "total_spots", "occupancy_rate"],
            "units": {"occupied_spots": "count", "total_spots": "count", "occupancy_rate": "%"}
        },
        "weather": {
            "metrics": ["temperature", "humidity", "pressure", "wind_speed", "precipitation"],
            "units": {"temperature": "°C", "humidity": "%", "pressure": "hPa", "wind_speed": "m/s", "precipitation": "mm/h"}
        },
        "energy": {
            "metrics": ["power_consumption", "voltage", "current", "power_factor"],
            "units": {"power_consumption": "kW", "voltage": "V", "current": "A", "power_factor": "0-1"}
        }
    }
    
    def __init__(self):
        """Initialize sensor data generator."""
        self.sensor_id_counter = 0
        self.base_values = self._initialize_base_values()
    
    def _initialize_base_values(self) -> Dict[str, float]:
        """Initialize base values for realistic variation."""
        return {
            "pm25": 25.0,
            "pm10": 40.0,
            "no2": 30.0,
            "co2": 400.0,
            "temperature": 15.0,
            "humidity": 65.0,
            "pressure": 1013.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "vehicle_count": 500.0,
            "average_speed": 45.0,
            "congestion_level": 3.0,
            "occupied_spots": 150.0,
            "total_spots": 200.0,
            "power_consumption": 50.0,
            "voltage": 230.0,
            "current": 15.0,
            "power_factor": 0.95
        }
    
    def generate_sensor_reading(self, sensor_type: str = None) -> Dict[str, Any]:
        """
        Generate a single sensor reading.
        
        Args:
            sensor_type: Type of sensor (if None, random)
            
        Returns:
            Sensor reading dictionary
        """
        if sensor_type is None:
            sensor_type = random.choice(list(self.SENSOR_TYPES.keys()))
        
        self.sensor_id_counter += 1
        
        city = random.choice(self.CITIES)
        district = random.choice(self.DISTRICTS)
        
        # Generate location
        base_lat = 52.2297  # Warsaw coordinates
        base_lon = 21.0122
        location = {
            "lat": round(base_lat + random.uniform(-0.15, 0.15), 6),
            "lon": round(base_lon + random.uniform(-0.15, 0.15), 6)
        }
        
        # Generate metrics for this sensor type
        metrics = self._generate_metrics(sensor_type)
        
        # Generate timestamp
        timestamp = datetime.utcnow()
        
        # Build sensor reading
        reading = {
            "sensor_id": f"{sensor_type.upper()}-{self.sensor_id_counter:06d}",
            "sensor_type": sensor_type,
            "city": city,
            "district": district,
            "location": location,
            "timestamp": timestamp.isoformat(),
            "metrics": metrics,
            "metadata": {
                "battery_level": round(random.uniform(20, 100), 1),
                "signal_strength": round(random.uniform(-90, -30), 1),
                "firmware_version": f"v{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 20)}",
                "last_calibration": (timestamp - timedelta(days=random.randint(1, 90))).isoformat()
            }
        }
        
        return reading
    
    def _generate_metrics(self, sensor_type: str) -> Dict[str, Any]:
        """Generate realistic metric values for sensor type."""
        sensor_config = self.SENSOR_TYPES[sensor_type]
        metrics = {}
        
        current_hour = datetime.utcnow().hour
        is_rush_hour = current_hour in [7, 8, 9, 16, 17, 18]
        is_night = current_hour >= 22 or current_hour <= 6
        
        for metric in sensor_config["metrics"]:
            base = self.base_values.get(metric, 50.0)
            
            # Add time-based variation
            if metric in ["vehicle_count", "average_speed", "congestion_level"]:
                if is_rush_hour:
                    base *= 1.8
                elif is_night:
                    base *= 0.3
            
            if metric in ["power_consumption"]:
                if is_night:
                    base *= 0.5
                else:
                    base *= 1.2
            
            # Add random variation
            variation = random.uniform(-0.15, 0.15)
            value = base * (1 + variation)
            
            # Apply constraints
            if metric == "occupancy_rate":
                occupied = metrics.get("occupied_spots", 150)
                total = metrics.get("total_spots", 200)
                value = round((occupied / total) * 100, 1) if total > 0 else 0
            elif metric == "congestion_level":
                value = max(0, min(10, value))
            elif metric == "humidity":
                value = max(0, min(100, value))
            elif metric == "power_factor":
                value = max(0, min(1, value))
            
            # Round appropriately
            if metric in ["vehicle_count", "occupied_spots", "total_spots"]:
                value = int(value)
            else:
                value = round(value, 2)
            
            metrics[metric] = {
                "value": value,
                "unit": sensor_config["units"][metric],
                "quality": random.choice(["good", "good", "good", "fair", "poor"])
            }
        
        return metrics


class SensorKafkaProducer:
    """Kafka producer for sensor data."""
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "smart-city-sensors"
    ):
        """
        Initialize Kafka producer for sensors.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
            topic: Kafka topic
        """
        self.topic = topic
        self.generator = SensorDataGenerator()
        
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            logger.info(f"Sensor Kafka producer initialized for topic: {self.topic}")
        except KafkaError as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise
    
    def send_reading(self, reading: Dict[str, Any]) -> None:
        """Send a sensor reading to Kafka."""
        try:
            key = f"{reading['city']}:{reading['sensor_type']}"
            future = self.producer.send(self.topic, key=key, value=reading)
            record_metadata = future.get(timeout=10)
            logger.debug(
                f"Sent {reading['sensor_id']} to partition {record_metadata.partition}"
            )
        except KafkaError as e:
            logger.error(f"Failed to send reading: {e}")
            raise
    
    def produce_continuous(
        self,
        sensors_per_second: float = 10.0,
        duration_seconds: int = None,
        sensor_distribution: Dict[str, float] = None
    ):
        """
        Continuously produce sensor readings.
        
        Args:
            sensors_per_second: Rate of sensor reading generation
            duration_seconds: Duration to run (None = infinite)
            sensor_distribution: Distribution of sensor types (default: equal)
        """
        if sensor_distribution is None:
            # Equal distribution
            sensor_types = list(SensorDataGenerator.SENSOR_TYPES.keys())
            sensor_distribution = {st: 1.0 / len(sensor_types) for st in sensor_types}
        
        logger.info(f"Starting sensor production at {sensors_per_second} readings/sec")
        logger.info(f"Sensor distribution: {sensor_distribution}")
        
        interval = 1.0 / sensors_per_second
        start_time = time.time()
        readings_sent = 0
        
        try:
            while True:
                # Choose sensor type based on distribution
                sensor_type = random.choices(
                    list(sensor_distribution.keys()),
                    weights=list(sensor_distribution.values())
                )[0]
                
                reading = self.generator.generate_sensor_reading(sensor_type)
                self.send_reading(reading)
                readings_sent += 1
                
                if readings_sent % 100 == 0:
                    logger.info(f"Sent {readings_sent} sensor readings")
                
                # Check duration
                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    break
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("Producer stopped by user")
        finally:
            self.close()
        
        elapsed = time.time() - start_time
        logger.info(
            f"Sent {readings_sent} readings in {elapsed:.2f} seconds "
            f"({readings_sent/elapsed:.2f} readings/sec)"
        )
    
    def close(self):
        """Close producer."""
        logger.info("Flushing and closing producer...")
        self.producer.flush()
        self.producer.close()


def main():
    """Main entry point."""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="Smart City Sensor Kafka Producer")
    parser.add_argument(
        "--bootstrap-servers",
        default=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        help="Kafka bootstrap servers"
    )
    parser.add_argument(
        "--topic",
        default="smart-city-sensors",
        help="Kafka topic"
    )
    parser.add_argument(
        "--rate",
        type=float,
        default=10.0,
        help="Readings per second"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=None,
        help="Duration in seconds"
    )
    
    args = parser.parse_args()
    
    producer = SensorKafkaProducer(
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic
    )
    
    producer.produce_continuous(
        sensors_per_second=args.rate,
        duration_seconds=args.duration
    )


if __name__ == "__main__":
    main()
