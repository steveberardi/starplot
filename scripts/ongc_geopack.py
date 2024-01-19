import os
from pathlib import Path

import geopandas as gpd
import pandas as pd

from shapely.geometry import Polygon, MultiPolygon


HERE = Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "raw" / "ongc" / "outlines"

CRS = "+ellps=sphere +f=0 +proj=latlong +axis=wnu +a=6378137 +no_defs"

def parse(filename):
    designation, level = filename.split('_')

    if designation.startswith('IC'):
        ic = designation[2:]
    else:
        ic = None
    

    if designation.startswith('NGC'):
        ngc = designation[3:]
    else:
        ngc = None

    return designation, ic, ngc


def walk_files(path=DATA_PATH):
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            yield Path(os.path.join(dirpath, filename))


d = {'designation': [], 'ic': [], 'ngc': [], 'geometry': []}


for f in walk_files():
    designation, ic, ngc = parse(f.name)

    if designation in d['designation']:
        continue

    dso_df = pd.read_csv(f, sep='\t')
    polygons = []
    current_poly = []

    for i, row in dso_df.iterrows():
        cont_flag = row['Cont_Flag']
        ra = row["RAJ2000"]
        dec = row["DEJ2000"]
        current_poly.append([ra, dec])

        if cont_flag == '*':
            # a * indicates this is the last point in the current polygon            
            polygons.append(current_poly)
            current_poly = []
            
    if len(polygons) > 1:
        dso_geom = MultiPolygon([Polygon(p) for p in polygons])
    else:
        dso_geom = Polygon(polygons[0])

    d['designation'].append(designation)
    d['geometry'].append(dso_geom)
    d['ic'].append(ic)
    d['ngc'].append(ngc)

    if not ic and not ngc:
        print(designation)

gdf = gpd.GeoDataFrame(d)

# gdf.simplify(10)
gdf.to_file(HERE.parent / "build" / "ngc.gpkg", driver="GPKG", crs=CRS)


# result = gpd.read_file(HERE.parent / "build" / "ngc.gpkg")
# print(result)
