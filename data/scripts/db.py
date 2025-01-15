from pathlib import Path

import duckdb
import ibis

from settings import BUILD_PATH, RAW_PATH

# HERE = Path(__file__).resolve().parent
# RAW_DATA_PATH = HERE / "raw"
# BUILD_PATH = HERE / "build"

# ibis.options.interactive = True
# con = ibis.duckdb.connect(BUILD_PATH / "sky.db")
# print(con.list_tables())

con = duckdb.connect(BUILD_PATH / "sky.db")
con.install_extension("spatial")
con.load_extension("spatial")

# Milky Way
milky_way_src = RAW_PATH / "milkyway.json"
con.sql("DROP TABLE IF EXISTS milky_way")
con.sql(
    f"CREATE TABLE milky_way AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{milky_way_src}'));"
)
con.sql("CREATE INDEX milky_way_geometry_idx ON milky_way USING RTREE (geometry);")

# Constellations
constellation_src = RAW_PATH / "constellations.json"
con.sql("DROP TABLE IF EXISTS constellations")
con.sql(
    f"CREATE TABLE constellations AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{constellation_src}'));"
)
con.sql(
    "CREATE INDEX constellations_boundary_idx ON constellations USING RTREE (geometry);"
)

constellation_borders_src = RAW_PATH / "constellation_borders.json"
con.sql("DROP TABLE IF EXISTS constellation_borders")
con.sql(
    f"CREATE TABLE constellation_borders AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{constellation_borders_src}'));"
)
con.sql(
    "CREATE INDEX constellation_borders_geometry_idx ON constellation_borders USING RTREE (geometry);"
)


# Deep Sky Objects
dso_src = BUILD_PATH / "ongc.gpkg"
con.sql("DROP TABLE IF EXISTS deep_sky_objects")
con.sql(
    f"CREATE TABLE deep_sky_objects AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{dso_src}'));"
)
con.sql("CREATE INDEX dso_idx ON deep_sky_objects USING RTREE (geometry);")
con.sql("CREATE UNIQUE INDEX dso_name_idx ON deep_sky_objects (name);")
con.sql("CREATE INDEX dso_messier_idx ON deep_sky_objects (m);")
con.sql("CREATE INDEX dso_ngc_idx ON deep_sky_objects (ngc);")
con.sql("CREATE INDEX dso_ic_idx ON deep_sky_objects (ic);")


star_designations_src = BUILD_PATH / "star_designations.parquet"
con.sql("DROP TABLE IF EXISTS star_designations")
con.sql(
    f"CREATE TABLE star_designations AS (SELECT * FROM read_parquet('{star_designations_src}') )"
)
con.sql("CREATE UNIQUE INDEX star_designations_hip_idx ON star_designations (hip);")
con.sql("CREATE INDEX star_designations_name_idx ON star_designations (name);")

