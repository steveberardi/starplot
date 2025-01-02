import duckdb
import ibis

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

# exit()
# con.drop_table("milky_way", force=True)


def read_gpack(filename):
    return gpd.read_file(
        filename,
        engine="pyogrio",
        use_arrow=True,
    )


ctr = 1
data = []
mw = read_gpack(DataFiles.MILKY_WAY.value)


def _prepare_polygon(p):
    points = list(zip(*p.boundary.coords.xy))
    # convert lon to RA and reverse so the coordinates are counterclockwise order
    return [(lon_to_ra(lon) * 15, dec) for lon, dec in reversed(points)]


for _, g in mw.iterrows():
    geometry = g.geometry.buffer(0.1)
    data.append({"id": ctr, "geometry": Polygon(_prepare_polygon(geometry))})
    ctr += 1


df = pd.DataFrame.from_records(data)
gdf = gpd.GeoDataFrame(
    df,
    geometry=df["geometry"],
    # crs=CRS,
)
# print(gdf)

gdf.to_file("build/mw.gpkg", driver="GPKG", index=True)  # crs=CRS,

# con.sql(
#     "CREATE TABLE milky_way AS (select * EXCLUDE geom, ST_GeomFromWKB(geom) AS geometry from ST_Read('build/mw.gpkg'));"
# )

con.read_geo("build/mw.gpkg", table_name="milky_way")


polygon = Polygon(
    [
        [0, 0],
        [180, 0],
        [180, 50],
        [0, 50],
        [0, 0],
    ]
)
mw = con.table("milky_way")

result = mw.filter(mw.geom.intersects(polygon))

print(result.to_pandas())


con = duckdb.connect(DataFiles.DATABASE.value)
con.install_extension("spatial")
con.load_extension("spatial")

# Milky Way
con.sql("DROP TABLE milky_way")
con.sql(
    "CREATE TABLE milky_way AS (select * EXCLUDE geom, geom AS geometry from ST_Read('build/mw.gpkg'));"
)
con.sql("CREATE INDEX milky_way_geometry_idx ON milky_way USING RTREE (geometry);")

# Constellations
con.sql("DROP TABLE constellations")
con.sql(
    f"CREATE TABLE constellations AS (select * EXCLUDE geom, geom AS geometry from ST_Read('{str(DataFiles.CONSTELLATIONS.value)}'));"
)
con.sql(
    "CREATE INDEX constellations_boundary_idx ON constellations USING RTREE (geometry);"
)

# Deep Sky Objects
con.sql("DROP TABLE deep_sky_objects")
con.sql(
    f"CREATE TABLE deep_sky_objects AS (select * EXCLUDE geom, geom AS geometry from ST_Read('temp/ongc.gpkg'));"
)
con.sql(
    "CREATE INDEX dso_idx ON deep_sky_objects USING RTREE (geometry);"
)






exit()
# create union of all Milky Way patches
gs = mw.geometry.to_crs(self._plate_carree)
mw_union = gs.buffer(0.1).unary_union.buffer(-0.1)
polygons = []

if mw_union.geom_type == "MultiPolygon":
    polygons.extend([_prepare_polygon(polygon) for polygon in mw_union.geoms])
else:
    polygons.append(_prepare_polygon(mw_union))

for polygon_points in polygons:
    self._polygon(
        points=polygon_points,
        style=style,
    )
