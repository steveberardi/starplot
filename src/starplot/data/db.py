from functools import cache

from ibis import duckdb

from starplot.config import settings
from starplot.data import DataFiles


@cache
def connect():
    connection = duckdb.connect(
        DataFiles.DATABASE, read_only=True
    )  # , threads=2, memory_limit="1GB"

    path = settings.data_path / "duckdb-extensions"
    connection.raw_sql(f"SET extension_directory = '{str(path)}';")

    connection.read_parquet(DataFiles.STAR_DESIGNATIONS, table_name="star_designations")
    connection.read_parquet(
        DataFiles.CONSTELLATION_NAMES, table_name="constellation_names"
    )
    connection.read_parquet(DataFiles.DSO_NAMES, table_name="dso_names")
    return connection
