import pandas as pd
import geopandas as gpd

from shapely.geometry import Point

CRS = "+ellps=sphere +f=0 +proj=latlong +axis=wnu +a=6378137 +no_defs"

df = pd.read_csv(
    "raw/stars.tycho-1.csv.gz",
    names=[
        "hip",
        "magnitude",
        "ra_hours",
        "dec_degrees",
        "parallax_mas",
        "ra_mas_per_year",
        "dec_mas_per_year",
        "bv",
    ],
    compression="gzip",
)

df["ra_degrees"] = df.apply(lambda row: row.ra_hours * 15, axis=1)

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.ra_degrees, df.dec_degrees),
    crs=CRS,
)

gdf.to_file("temp/tycho-1.gpkg", driver="GPKG", crs=CRS)

# df.to_parquet('temp/output.parquet', compression="gzip")
