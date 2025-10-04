"""
Dagster resources for database connections and configurations.
"""
from pathlib import Path
from dagster import ConfigurableResource
import duckdb

class DuckDBResource(ConfigurableResource):
    database_path: str = "data/analytics.duckdb"

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        return duckdb.connect(self.database_path)
