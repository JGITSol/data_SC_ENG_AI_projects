"""
Storage abstraction layer for S3/MinIO.

Handles data persistence to object storage for archival and analytics.
"""

import boto3
from botocore.exceptions import ClientError
import json
import logging
from datetime import datetime
from typing import Dict, Any, List,  Optional
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class S3StorageManager:
    """Manage S3/MinIO storage for sensor data."""
    
    def __init__(
        self,
        endpoint_url: str = None,
        access_key: str = None,
        secret_key: str = None,
        bucket_name: str = "smart-city-data",
        region: str = "us-east-1"
    ):
        """
        Initialize S3 storage manager.
        
        Args:
            endpoint_url: S3 endpoint (for MinIO)
            access_key: AWS access key
            secret_key: AWS secret key
            bucket_name: S3 bucket name
            region: AWS region
        """
        self.bucket_name = bucket_name
        
        # Get credentials from env if not provided
        if access_key is None:
            access_key = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
        if secret_key is None:
            secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
        if endpoint_url is None:
            endpoint_url = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        logger.info(f"S3 storage manager initialized for bucket: {bucket_name}")
        
        # Ensure bucket exists
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Create bucket if it doesn't exist."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket '{self.bucket_name}' exists")
        except ClientError:
            try:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            except ClientError as e:
                logger.error(f"Failed to create bucket: {e}")
                raise
    
    def upload_sensor_reading(
        self,
        reading: Dict[str, Any],
        prefix: str = "raw-data"
    ) -> str:
        """
        Upload a sensor reading to S3.
        
        Args:
            reading: Sensor reading dictionary
            prefix: S3 key prefix
            
        Returns:
            S3 key of uploaded object
        """
        # Build S3 key with partitioning
        timestamp = datetime.fromisoformat(reading["timestamp"].replace('Z', '+00:00'))
        sensor_type = reading["sensor_type"]
        city = reading["city"]
        
        key = (
           f"{prefix}/"
            f"sensor_type={sensor_type}/"
            f"city={city}/"
            f"year={timestamp.year}/"
            f"month={timestamp.month:02d}/"
            f"day={timestamp.day:02d}/"
            f"hour={timestamp.hour:02d}/"
            f"{reading['sensor_id']}_{timestamp.isoformat()}.json"
        )
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(reading),
                ContentType='application/json',
                Metadata={
                    'sensor_id': reading['sensor_id'],
                    'sensor_type': sensor_type,
                    'city': city
                }
            )
            logger.debug(f"Uploaded reading to: s3://{self.bucket_name}/{key}")
            return key
        except ClientError as e:
            logger.error(f"Failed to upload reading: {e}")
            raise
    
    def upload_aggregation(
        self,
        aggregation: Dict[str, Any],
        prefix: str = "aggregated-data"
    ) -> str:
        """
        Upload aggregated data to S3.
        
        Args:
            aggregation: Aggregation result
            prefix: S3 key prefix
            
        Returns:
            S3 key
        """
        timestamp = datetime.utcnow()
        agg_type = aggregation.get("aggregation_type", "unknown")
        city = aggregation.get("city", "unknown")
        
        key = (
            f"{prefix}/"
            f"type={agg_type}/"
            f"city={city}/"
            f"year={timestamp.year}/"
            f"month={timestamp.month:02d}/"
            f"day={timestamp.day:02d}/"
            f"agg_{timestamp.isoformat()}.json"
        )
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(aggregation),
                ContentType='application/json'
            )
            return key
        except ClientError as e:
            logger.error(f"Failed to upload aggregation: {e}")
            raise
    
    def list_objects(
        self,
        prefix: str = "",
        max_keys: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List objects in bucket.
        
        Args:
            prefix: Key prefix filter
            max_keys: Maximum number of keys to return
            
        Returns:
            List of object metadata
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            if 'Contents' not in response:
                return []
            
            return [
                {
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                }
                for obj in response['Contents']
            ]
        except ClientError as e:
            logger.error(f"Failed to list objects: {e}")
            raise
    
    def download_object(self, key: str) -> Dict[str, Any]:
        """
        Download and parse JSON object from S3.
        
        Args:
            key: S3 object key
            
        Returns:
            Parsed JSON data
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            data = json.loads(response['Body'].read().decode('utf-8'))
            return data
        except ClientError as e:
            logger.error(f"Failed to download object: {e}")
            raise
    
    def delete_object(self, key: str) -> bool:
        """
        Delete object from S3.
        
        Args:
            key: S3 object key
            
        Returns:
            True if successful
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            logger.info(f"Deleted object: {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete object: {e}")
            return False
    
    def get_bucket_stats(self) -> Dict[str, Any]:
        """
        Get bucket statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            # Count objects and total size
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name)
            
            total_objects = 0
            total_size = 0
            
            for page in pages:
                if 'Contents' in page:
                    total_objects += len(page['Contents'])
                    total_size += sum(obj['Size'] for obj in page['Contents'])
            
            return {
                'bucket_name': self.bucket_name,
                'total_objects': total_objects,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        except ClientError as e:
            logger.error(f"Failed to get bucket stats: {e}")
            raise
