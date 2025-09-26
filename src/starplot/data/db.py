from functools import cache

from ibis import duckdb

from starplot.config import settings
from starplot.data import DataFiles


@cache
def connect():
    connection = duckdb.connect(
        DataFiles.DATABASE, read_only=True
    )  # , threads=2, memory_limit="1GB"
    connection.raw_sql(
        f"SET extension_directory = '{str(settings.duckdb_extension_path)}';"
    )
    return connection
