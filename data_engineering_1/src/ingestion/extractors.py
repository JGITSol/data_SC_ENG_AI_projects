"""
Extractors for NYC Taxi and zone data from public sources.
"""
from pathlib import Path
import pandas as pd
import requests
import zipfile
import io
class TaxiDataExtractor:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    def extract(self, max_records: int = 100000) -> pd.DataFrame:
        url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2023-01.csv.gz"
        df = pd.read_csv(url, compression="gzip", nrows=max_records)
        return df
    def save(self, df: pd.DataFrame) -> Path:
        out_path = self.output_dir / "taxi_trips.parquet"
        df.to_parquet(out_path, engine="pyarrow", index=False)
        return out_path
class ZoneDataExtractor:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    def extract(self) -> pd.DataFrame:
        url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv"
        df = pd.read_csv(url)
        return df
    def save(self, df: pd.DataFrame) -> Path:
        out_path = self.output_dir / "zone_lookup.parquet"
        df.to_parquet(out_path, engine="pyarrow", index=False)
        return out_path
