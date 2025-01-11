import duckdb
import ibis

from starplot import settings
from starplot.data import DataFiles


CRS = "+ellps=sphere +f=0 +proj=latlong +axis=wnu +a=6378137 +no_defs"

con = ibis.duckdb.connect(DataFiles.DATABASE)

ibis.options.interactive = True

print(con.list_tables())

con = duckdb.connect(DataFiles.DATABASE)
con.install_extension("spatial")
con.load_extension("spatial")

# Milky Way
milky_way_src = str(settings.BUILD_PATH / "constellations.gpkg")
con.sql("DROP TABLE IF EXISTS milky_way")
con.sql(
    f"CREATE TABLE milky_way AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{milky_way_src}'));"
)
con.sql("CREATE INDEX milky_way_geometry_idx ON milky_way USING RTREE (geometry);")

# Constellations
constellation_src = str(settings.BUILD_PATH / "constellations.gpkg")
con.sql("DROP TABLE IF EXISTS constellations")
con.sql(
    f"CREATE TABLE constellations AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{constellation_src}'));"
)
con.sql(
    "CREATE INDEX constellations_boundary_idx ON constellations USING RTREE (geometry);"
)

con.sql("DROP TABLE IF EXISTS constellation_borders")
con.sql(
    f"CREATE TABLE constellation_borders AS (select * EXCLUDE geom, geom AS geometry from ST_Read('temp/constellation_borders_new.json'));"
)
con.sql(
    "CREATE INDEX constellation_borders_geometry_idx ON constellation_borders USING RTREE (geometry);"
)


# Deep Sky Objects
dso_src = str(settings.BUILD_PATH / "ongc.gpkg")
con.sql("DROP TABLE IF EXISTS deep_sky_objects")
con.sql(
    f"CREATE TABLE deep_sky_objects AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{dso_src}'));"
)
con.sql("CREATE INDEX dso_idx ON deep_sky_objects USING RTREE (geometry);")

con.sql("DROP TABLE IF EXISTS star_designations")
con.sql(
    "CREATE TABLE star_designations AS (SELECT * FROM read_parquet('temp/star_designations.parquet') )"
)
con.sql("CREATE UNIQUE INDEX star_designations_hip_idx ON star_designations (hip);")
con.sql("CREATE UNIQUE INDEX star_designations_name_idx ON star_designations (name);")
