import time
import json
from pathlib import Path

from shapely import LineString

from starplot import ConstellationBorder
from starplot.data import Catalog

from data_settings import RAW_PATH, BUILD_PATH

def constellation_borders():
    ctr = 0
    with open(RAW_PATH / "constellation_borders.json", "r") as infile:
        data = json.loads(infile.read())

        for feature in data["features"]:
            ctr += 1
            coordinates = feature["geometry"]["coordinates"]
            geometry = LineString(coordinates)
            ra = round(geometry.centroid.x, 4)
            dec = round(geometry.centroid.y, 4)

            yield ConstellationBorder(
                pk=ctr,
                ra=ra,
                dec=dec,
                geometry=geometry,
            )


def build():
    print("Building Constellation Border Catalog...")
    time_start = time.time()

    catalog = Catalog(path=BUILD_PATH / "constellation-borders.parquet")
    catalog.build(
        objects=constellation_borders(),
        chunk_size=200_000,
        columns=[
            "pk",
            "ra",
            "dec",
            "geometry",
        ],
        partition_columns=[],
        compression="none",
        row_group_size=100_000,
    )

    duration = time.time() - time_start
    print(f"Done. {duration:.000f}s")


if __name__ == "__main__":
    build()
