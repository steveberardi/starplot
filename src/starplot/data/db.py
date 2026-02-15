from ibis import duckdb

from starplot.config import settings
from starplot.data import DataFiles


NAME_TABLES = {
    "star_designations": DataFiles.STAR_DESIGNATIONS,
    "constellation_names": DataFiles.CONSTELLATION_NAMES,
    "dso_names": DataFiles.DSO_NAMES,
}


def connect():
    path = settings.data_path / "duckdb-extensions"
    connection = duckdb.connect()
    connection.raw_sql(f"SET extension_directory = '{str(path)}';")
    connection.raw_sql("INSTALL spatial;")
    connection.load_extension("spatial")

    missing_name_tables = set(NAME_TABLES.keys()) - set(connection.list_tables())

    for table_name in missing_name_tables:
        connection.read_parquet(NAME_TABLES[table_name], table_name=table_name)

    return connection
