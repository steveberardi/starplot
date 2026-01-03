import os
import shutil

import duckdb

from starplot.data import DataFiles

import star_designations, constellation_names, dso_names
from data_settings import BUILD_PATH, RAW_PATH

db_path = BUILD_PATH / "sky.db"


def build_all():
    # remove build directory, recreate it
    if os.path.exists(BUILD_PATH):
        shutil.rmtree(BUILD_PATH)
    os.makedirs(BUILD_PATH, exist_ok=True)

    star_designations.build()
    constellation_names.build()
    dso_names.build()

    build_db()

    # Copy database to starplot data library
    shutil.copy(db_path, DataFiles.DATABASE)
    shutil.copy(BUILD_PATH / "star_designations.parquet", DataFiles.STAR_DESIGNATIONS)
    shutil.copy(
        BUILD_PATH / "constellation_names.parquet", DataFiles.CONSTELLATION_NAMES
    )
    shutil.copy(BUILD_PATH / "dso_names.parquet", DataFiles.DSO_NAMES)


def build_db():
    con = duckdb.connect(db_path)
    con.install_extension("spatial")
    con.load_extension("spatial")

    # Milky Way
    milky_way_src = RAW_PATH / "milkyway.json"
    con.execute(
        (
            "DROP TABLE IF EXISTS milky_way;"
            f"CREATE TABLE milky_way AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{milky_way_src}'));"
            "CREATE INDEX milky_way_geometry_idx ON milky_way USING RTREE (geometry);"
        ),
    )

    constellation_borders_src = RAW_PATH / "constellation_borders.json"
    con.sql(
        (
            "DROP TABLE IF EXISTS constellation_borders;"
            f"CREATE TABLE constellation_borders AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{constellation_borders_src}'));"
            "CREATE INDEX constellation_borders_geometry_idx ON constellation_borders USING RTREE (geometry);"
        )
    )

    # star_designations_src = BUILD_PATH / "star_designations.parquet"
    # con.sql(
    #     (
    #         "DROP TABLE IF EXISTS star_designations;"
    #         f"CREATE TABLE star_designations AS (SELECT * FROM read_parquet('{star_designations_src}') );"
    #         "CREATE INDEX star_designations_hip_idx ON star_designations (hip);"
    #         "CREATE INDEX star_designations_name_idx ON star_designations (name);"
    #     )
    # )

    # constellation_names_src = BUILD_PATH / "constellation_names.parquet"
    # con.sql(
    #     (
    #         "DROP TABLE IF EXISTS constellation_names;"
    #         f"CREATE TABLE constellation_names AS (SELECT * FROM read_parquet('{constellation_names_src}') );"
    #         "CREATE INDEX constellation_names_iau_id_idx ON constellation_names (iau_id);"
    #     )
    # )

    # dso_names_src = BUILD_PATH / "dso_names.parquet"
    # con.sql(
    #     (
    #         "DROP TABLE IF EXISTS dso_names;"
    #         f"CREATE TABLE dso_names AS (SELECT * FROM read_parquet('{dso_names_src}') );"
    #         "CREATE INDEX dso_names_open_ngc_name_idx ON dso_names (open_ngc_name);"
    #     )
    # )

    print("Sky.db created!")
    con.close()


if __name__ == "__main__":
    build_all()
