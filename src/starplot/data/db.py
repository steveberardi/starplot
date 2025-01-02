from functools import cache

import ibis

from starplot.data import DUCKDB_EXTENSION_PATH, DataFiles


@cache
def connect():
    connection = ibis.duckdb.connect(DataFiles.DATABASE.value, read_only=True)
    connection.raw_sql(f"SET extension_directory = '{str(DUCKDB_EXTENSION_PATH)}';")
    return connection
