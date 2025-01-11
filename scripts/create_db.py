import duckdb
import ibis

from starplot.data import DataFiles


CRS = "+ellps=sphere +f=0 +proj=latlong +axis=wnu +a=6378137 +no_defs"

con = ibis.duckdb.connect(DataFiles.DATABASE)

ibis.options.interactive = True

print(con.list_tables())

con = duckdb.connect(DataFiles.DATABASE)
con.install_extension("spatial")
con.load_extension("spatial")

# Milky Way
con.sql("DROP TABLE IF EXISTS milky_way")
con.sql(
    "CREATE TABLE milky_way AS (select * EXCLUDE geom, geom AS geometry from ST_Read('build/mw.gpkg'));"
)
con.sql("CREATE INDEX milky_way_geometry_idx ON milky_way USING RTREE (geometry);")

# Constellations
con.sql("DROP TABLE IF EXISTS constellations")
con.sql(
    f"CREATE TABLE constellations AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{str(DataFiles.CONSTELLATIONS)}'));"
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
con.sql("DROP TABLE IF EXISTS deep_sky_objects")
con.sql(
    f"CREATE TABLE deep_sky_objects AS (select * EXCLUDE geom, geom AS geometry from ST_Read('temp/ongc.gpkg'));"
)
con.sql("CREATE INDEX dso_idx ON deep_sky_objects USING RTREE (geometry);")

con.sql("DROP TABLE IF EXISTS star_designations")
con.sql(
    "CREATE TABLE star_designations AS (SELECT * FROM read_parquet('temp/star_designations.parquet') )"
)
con.sql("CREATE UNIQUE INDEX star_designations_hip_idx ON star_designations (hip);")
con.sql("CREATE UNIQUE INDEX star_designations_name_idx ON star_designations (name);")

# Stars
# con.sql("DROP TABLE IF EXISTS stars")
# con.sql(
#     f"CREATE TABLE stars AS (select * EXCLUDE geom, geom AS geometry from ST_Read('build/stars.gpkg'));"
# )
# con.sql("CREATE INDEX star_idx ON stars USING RTREE (geometry);")
