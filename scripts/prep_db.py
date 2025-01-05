import duckdb
import ibis
import time

from shapely import Polygon
import geopandas as gpd
import pandas as pd

from starplot.data import DataFiles
from starplot.utils import lon_to_ra

CRS = "+ellps=sphere +f=0 +proj=latlong +axis=wnu +a=6378137 +no_defs"

con = ibis.duckdb.connect(DataFiles.DATABASE.value)

# con = duckdb.connect(DataFiles.DATABASE.value)
# con.install_extension("spatial")
# con.load_extension("spatial")

ibis.options.interactive = True

print(con.list_tables())

# for _, g in mw.iterrows():
#     geometry = g.geometry.buffer(0.1)
#     data.append({"id": ctr, "geometry": Polygon(_prepare_polygon(geometry))})
#     ctr += 1


# df = pd.DataFrame.from_records(data)
# gdf = gpd.GeoDataFrame(
#     df,
#     geometry=df["geometry"],
#     # crs=CRS,
# )
# # print(gdf)

# gdf.to_file("build/mw.gpkg", driver="GPKG", index=True)  # crs=CRS,

# # con.sql(
# #     "CREATE TABLE milky_way AS (select * EXCLUDE geom, ST_GeomFromWKB(geom) AS geometry from ST_Read('build/mw.gpkg'));"
# # )

# con.read_geo("build/mw.gpkg", table_name="milky_way")


# polygon = Polygon(
#     [
#         [0, 0],
#         [180, 0],
#         [180, 50],
#         [0, 50],
#         [0, 0],
#     ]
# )
# mw = con.table("milky_way")

# result = mw.filter(mw.geom.intersects(polygon))

# print(result.to_pandas())


con = duckdb.connect(DataFiles.DATABASE.value)
con.install_extension("spatial")
con.load_extension("spatial")

# start = time.time()
# result = con.sql("SELECT * from stars where magnitude < 6").df()
# print(result)
# print(time.time() - start)
# exit()


# Milky Way
con.sql("DROP TABLE IF EXISTS milky_way")
con.sql(
    "CREATE TABLE milky_way AS (select * EXCLUDE geom, geom AS geometry from ST_Read('build/mw.gpkg'));"
)
con.sql("CREATE INDEX milky_way_geometry_idx ON milky_way USING RTREE (geometry);")

# Constellations
con.sql("DROP TABLE IF EXISTS constellations")
con.sql(
    f"CREATE TABLE constellations AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{str(DataFiles.CONSTELLATIONS.value)}'));"
)
con.sql(
    "CREATE INDEX constellations_boundary_idx ON constellations USING RTREE (geometry);"
)

con.sql("DROP TABLE IF EXISTS constellation_borders")
con.sql(
    f"CREATE TABLE constellation_borders AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{str(DataFiles.CONSTELLATION_BORDERS.value)}'));"
)
con.sql("CREATE INDEX constellation_borders_geometry_idx ON constellation_borders USING RTREE (geometry);")


# Deep Sky Objects
con.sql("DROP TABLE IF EXISTS deep_sky_objects")
con.sql(
    f"CREATE TABLE deep_sky_objects AS (select * EXCLUDE geom, geom AS geometry from ST_Read('temp/ongc.gpkg'));"
)
con.sql("CREATE INDEX dso_idx ON deep_sky_objects USING RTREE (geometry);")


# Stars
# con.sql("DROP TABLE IF EXISTS stars")
# con.sql(
#     f"CREATE TABLE stars AS (select * EXCLUDE geom, geom AS geometry from ST_Read('build/stars.gpkg'));"
# )
# con.sql("CREATE INDEX star_idx ON stars USING RTREE (geometry);")
