import time
import json
from pathlib import Path

from shapely import Polygon

from starplot import MilkyWay
from starplot.data import Catalog

from data_settings import BUILD_PATH, RAW_PATH


def milky_ways():
    ctr = 0
    with open(RAW_PATH / "milkyway.json", "r") as infile:
        data = json.loads(infile.read())

        for feature in data["features"]:
            ctr += 1
            coordinates = feature["geometry"]["coordinates"]
            geometry = Polygon(coordinates[0])
            ra = round(geometry.centroid.x, 4)
            dec = round(geometry.centroid.y, 4)

            yield MilkyWay(
                pk=ctr,
                ra=ra,
                dec=dec,
                geometry=geometry,
            )


def build():
    print("Building Milky Way Catalog...")
    time_start = time.time()

    catalog = Catalog(path=BUILD_PATH / "milky_way.parquet")
    catalog.build(
        objects=milky_ways(),
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

    # all_stars = [s for s in Star.all(catalog=catalog)]
    # assert len(all_stars) == 119_625

    # sirius = Star.get(name="Sirius", catalog=catalog)
    # assert sirius.magnitude == -1.44
    # assert sirius.hip == 32349
    # assert sirius.constellation_id == "cma"

    duration = time.time() - time_start
    print(f"Done. {duration:.000f}s")


if __name__ == "__main__":
    build()
