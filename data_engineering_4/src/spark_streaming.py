"""
Spark Streaming job for processing smart city sensor data.

Consumes sensor readings from Kafka, processes them in micro-batches,
performs aggregations, and stores results in PostgreSQL and S3.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json, col, window, avg, count, max as spark_max, min as spark_min,
    current_timestamp, unix_timestamp, to_timestamp, expr
)
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, TimestampType,
    IntegerType, MapType
)
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartCitySensorProcessor:
    """Spark Streaming processor for smart city sensor data."""
    
    def __init__(
        self,
        app_name: str = "SmartCitySensorProcessor",
        kafka_bootstrap_servers: str = "localhost:9092",
        kafka_topic: str = "smart-city-sensors",
        checkpoint_location: str = "/tmp/spark-checkpoints",
        output_mode: str = "append"
    ):
        """
        Initialize Spark Streaming processor.
        
        Args:
            app_name: Spark application name
            kafka_bootstrap_servers: Kafka servers
            kafka_topic: Kafka topic to consume
            checkpoint_location: Checkpoint directory
            output_mode: Output mode (append/update/complete)
        """
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_topic = kafka_topic
        self.checkpoint_location = checkpoint_location
        self.output_mode = output_mode
        
        # Initialize Spark session
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.jars.packages", 
                   "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,"
                   "org.postgresql:postgresql:42.6.0,"
                   "org.apache.hadoop:hadoop-aws:3.3.4") \
            .config("spark.sql.streaming.checkpointLocation", checkpoint_location) \
            .config("spark.sql.adaptive.enabled", "true") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        logger.info(f"Spark session created: {app_name}")
    
    def define_schema(self) -> StructType:
        """Define schema for sensor readings."""
        return StructType([
            StructField("sensor_id", StringType(), True),
            StructField("sensor_type", StringType(), True),
            StructField("city", StringType(), True),
            StructField("district", StringType(), True),
            StructField("location", StructType([
                StructField("lat", DoubleType(), True),
                StructField("lon", DoubleType(), True)
            ]), True),
            StructField("timestamp", StringType(), True),
            StructField("metrics", MapType(StringType(), StructType([
                StructField("value", DoubleType(), True),
                StructField("unit", StringType(), True),
                StructField("quality", StringType(), True)
            ])), True),
            StructField("metadata", StructType([
                StructField("battery_level", DoubleType(), True),
                StructField("signal_strength", DoubleType(), True),
                StructField("firmware_version", StringType(), True),
                StructField("last_calibration", StringType(), True)
            ]), True)
        ])
    
    def read_from_kafka(self):
        """Read streaming data from Kafka."""
        logger.info(f"Reading from Kafka topic: {self.kafka_topic}")
        
        df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_bootstrap_servers) \
            .option("subscribe", self.kafka_topic) \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", "false") \
            .load()
        
        # Parse JSON
        schema = self.define_schema()
        parsed_df = df.select(
            from_json(col("value").cast("string"), schema).alias("data"),
            col("timestamp").alias("kafka_timestamp")
        ).select("data.*", "kafka_timestamp")
        
        # Convert timestamp string to timestamp type
        parsed_df = parsed_df.withColumn(
            "event_timestamp",
            to_timestamp(col("timestamp"))
        )
        
        return parsed_df
    
    def process_air_quality_stream(self, df):
        """Process air quality sensor stream."""
        air_quality_df = df.filter(col("sensor_type") == "air_quality")
        
        # Extract PM2.5 and PM10 values
        processed = air_quality_df.withColumn(
            "pm25_value",
            col("metrics.pm25.value")
        ).withColumn(
            "pm10_value",
            col("metrics.pm10.value")
        ).withColumn(
            "no2_value",
            col("metrics.no2.value")
        ).withColumn(
            "co2_value",
            col("metrics.co2.value")
        )
        
        # Windowed aggregations (5-minute windows, 1-minute slide)
        aggregated = processed \
            .withWatermark("event_timestamp", "10 minutes") \
            .groupBy(
                window(col("event_timestamp"), "5 minutes", "1 minute"),
                col("city"),
                col("district")
            ) \
            .agg(
                avg("pm25_value").alias("avg_pm25"),
                spark_max("pm25_value").alias("max_pm25"),
                avg("pm10_value").alias("avg_pm10"),
                spark_max("pm10_value").alias("max_pm10"),
                avg("no2_value").alias("avg_no2"),
                avg("co2_value").alias("avg_co2"),
                count("*").alias("reading_count")
            ) \
            .withColumn("aggregation_type", expr("'air_quality'")) \
            .withColumn("processing_time", current_timestamp())
        
        return aggregated
    
    def process_traffic_stream(self, df):
        """Process traffic sensor stream."""
        traffic_df = df.filter(col("sensor_type") == "traffic")
        
        processed = traffic_df.withColumn(
            "vehicle_count",
            col("metrics.vehicle_count.value")
        ).withColumn(
            "avg_speed",
            col("metrics.average_speed.value")
        ).withColumn(
            "congestion",
            col("metrics.congestion_level.value")
        )
        
        # Windowed aggregations
        aggregated = processed \
            .withWatermark("event_timestamp", "10 minutes") \
            .groupBy(
                window(col("event_timestamp"), "5 minutes", "1 minute"),
                col("city"),
                col("district")
            ) \
            .agg(
                avg("vehicle_count").alias("avg_vehicle_count"),
                avg("avg_speed").alias("avg_speed"),
                avg("congestion").alias("avg_congestion"),
                count("*").alias("reading_count")
            ) \
            .withColumn("aggregation_type", expr("'traffic'")) \
            .withColumn("processing_time", current_timestamp())
        
        return aggregated
    
    def process_energy_stream(self, df):
        """Process energy meter stream."""
        energy_df = df.filter(col("sensor_type") == "energy")
        
        processed = energy_df.withColumn(
            "power_consumption",
            col("metrics.power_consumption.value")
        ).withColumn(
            "voltage",
            col("metrics.voltage.value")
        ).withColumn(
            "current",
            col("metrics.current.value")
        )
        
        # Windowed aggregations
        aggregated = processed \
            .withWatermark("event_timestamp", "10 minutes") \
            .groupBy(
                window(col("event_timestamp"), "15 minutes", "5 minutes"),
                col("city"),
                col("district")
            ) \
            .agg(
                avg("power_consumption").alias("avg_power_consumption"),
                spark_max("power_consumption").alias("max_power_consumption"),
                avg("voltage").alias("avg_voltage"),
                avg("current").alias("avg_current"),
                count("*").alias("reading_count")
            ) \
            .withColumn("aggregation_type", expr("'energy'")) \
            .withColumn("processing_time", current_timestamp())
        
        return aggregated
    
    def write_to_postgres(self, df, table_name: str):
        """Write stream to PostgreSQL."""
        jdbc_url = os.getenv("JDBC_URL", "jdbc:postgresql://localhost:5432/smartcity")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "postgres")
        
        query = df.writeStream \
            .outputMode(self.output_mode) \
            .foreachBatch(
                lambda batch_df, batch_id: self._write_batch_to_postgres(
                    batch_df, batch_id, table_name, jdbc_url, db_user, db_password
                )
            ) \
            .option("checkpointLocation", f"{self.checkpoint_location}/{table_name}") \
            .start()
        
        return query
    
    def _write_batch_to_postgres(self, batch_df, batch_id, table_name, jdbc_url, user, password):
        """Write a micro-batch to PostgreSQL."""
        if batch_df.count() > 0:
            logger.info(f"Writing batch {batch_id} to {table_name}: {batch_df.count()} records")
            
            batch_df.write \
                .format("jdbc") \
                .option("url", jdbc_url) \
                .option("dbtable", table_name) \
                .option("user", user) \
                .option("password", password) \
                .option("driver", "org.postgresql.Driver") \
                .mode("append") \
                .save()
    
    def write_to_s3(self, df, s3_path: str, partition_cols: list = None):
        """Write stream to S3 in Parquet format."""
        if partition_cols is None:
            partition_cols = ["city", "aggregation_type"]
        
        query = df.writeStream \
            .outputMode(self.output_mode) \
            .format("parquet") \
            .option("path", s3_path) \
            .option("checkpointLocation", f"{self.checkpoint_location}/s3") \
            .partitionBy(*partition_cols) \
            .start()
        
        return query
    
    def write_to_console(self, df, output_mode: str = "append"):
        """Write stream to console for debugging."""
        query = df.writeStream \
            .outputMode(output_mode) \
            .format("console") \
            .option("truncate", "false") \
            .start()
        
        return query
    
    def run(self):
        """Run the Spark Streaming job."""
        logger.info("Starting Spark Streaming job...")
        
        # Read from Kafka
        sensor_stream = self.read_from_kafka()
        
        # Process different sensor types
        air_quality_agg = self.process_air_quality_stream(sensor_stream)
        traffic_agg = self.process_traffic_stream(sensor_stream)
        energy_agg = self.process_energy_stream(sensor_stream)
        
        # Write to PostgreSQL
        query1 = self.write_to_postgres(air_quality_agg, "air_quality_agg")
        query2 = self.write_to_postgres(traffic_agg, "traffic_agg")
        query3 = self.write_to_postgres(energy_agg, "energy_agg")
        
        # Optionally write to S3 (if configured)
        s3_path = os.getenv("S3_OUTPUT_PATH")
        if s3_path:
            all_agg = air_quality_agg.union(traffic_agg).union(energy_agg)
            query4 = self.write_to_s3(all_agg, s3_path)
        
        # Wait for termination
        logger.info("Streaming queries started. Waiting for termination...")
        self.spark.streams.awaitAnyTermination()
    
    def stop(self):
        """Stop Spark session."""
        logger.info("Stopping Spark session...")
        self.spark.stop()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart City Sensor Spark Streaming")
    parser.add_argument(
        "--kafka-servers",
        default=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        help="Kafka bootstrap servers"
    )
    parser.add_argument(
        "--kafka-topic",
        default="smart-city-sensors",
        help="Kafka topic"
    )
    parser.add_argument(
        "--checkpoint",
        default="/tmp/spark-checkpoints",
        help="Checkpoint location"
    )
    
    args = parser.parse_args()
    
    processor = SmartCitySensorProcessor(
        kafka_bootstrap_servers=args.kafka_servers,
        kafka_topic=args.kafka_topic,
        checkpoint_location=args.checkpoint
    )
    
    try:
        processor.run()
    except KeyboardInterrupt:
        logger.info("Streaming job interrupted by user")
    finally:
        processor.stop()


if __name__ == "__main__":
    main()
