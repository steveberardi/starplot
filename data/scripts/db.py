import os
import shutil

import duckdb

from starplot import Star, DSO, Constellation
from starplot.data import DataFiles

import bigsky_mag11, constellations, dsos, star_designations
from data_settings import BUILD_PATH, RAW_PATH

db_path = BUILD_PATH / "sky.db"


def build_all():
    # remove build directory, recreate it
    if os.path.exists(BUILD_PATH):
        shutil.rmtree(BUILD_PATH)
    os.makedirs(BUILD_PATH, exist_ok=True)

    bigsky_mag11.build()
    constellations.build()
    dsos.build()
    star_designations.build()

    build_db()
    copy_to_library()
    assert_counts()


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

    # Constellations
    constellation_src = BUILD_PATH / "constellations.json"
    con.sql(
        (
            "DROP TABLE IF EXISTS constellations;"
            f"CREATE TABLE constellations AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{constellation_src}'));"
            "CREATE INDEX constellations_boundary_idx ON constellations USING RTREE (geometry);"
        )
    )

    constellation_borders_src = RAW_PATH / "constellation_borders.json"
    con.sql(
        (
            "DROP TABLE IF EXISTS constellation_borders;"
            f"CREATE TABLE constellation_borders AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{constellation_borders_src}'));"
            "CREATE INDEX constellation_borders_geometry_idx ON constellation_borders USING RTREE (geometry);"
        )
    )

    # Deep Sky Objects
    dso_src = BUILD_PATH / "ongc.json"
    con.sql(
        (
            "DROP TABLE IF EXISTS deep_sky_objects;"
            f"CREATE TABLE deep_sky_objects AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{dso_src}'));"
            "CREATE INDEX dso_idx ON deep_sky_objects USING RTREE (geometry);"
            "CREATE INDEX dso_name_idx ON deep_sky_objects (name);"
            "CREATE INDEX dso_messier_idx ON deep_sky_objects (m);"
            "CREATE INDEX dso_ngc_idx ON deep_sky_objects (ngc);"
            "CREATE INDEX dso_ic_idx ON deep_sky_objects (ic);"
        )
    )

    star_designations_src = BUILD_PATH / "star_designations.parquet"
    con.sql(
        (
            "DROP TABLE IF EXISTS star_designations;"
            f"CREATE TABLE star_designations AS (SELECT * FROM read_parquet('{star_designations_src}') );"
            "CREATE INDEX star_designations_hip_idx ON star_designations (hip);"
            "CREATE INDEX star_designations_name_idx ON star_designations (name);"
        )
    )

    print("Sky.db created!")
    con.close()


def copy_to_library():
    # Copy database to starplot data library
    shutil.copy(db_path, DataFiles.DATABASE)


def assert_counts():
    # Assert correct number of objects were imported
    all_stars = Star.find(where=[])
    print("Stars = " + str(len(all_stars)))
    assert len(all_stars) == 981_853

    all_dsos = DSO.find(where=[])
    print("DSOs = " + str(len(all_dsos)))
    assert len(all_dsos) == 14_036

    all_constellations = Constellation.find(where=[])
    print("Constellations = " + str(len(all_constellations)))
    assert len(all_constellations) == 89


if __name__ == "__main__":
    build_all()
