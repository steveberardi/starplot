# Building Custom Catalogs




::: starplot.data.Catalog
    options:
        inherited_members: true
        show_docstring_attributes: true
        show_root_heading: true



## Building Catalogs

Building a new catalog is a two-step process:

1. Creating a reader that reads some source data and yields sky objects
2. Calling the class method `Catalog.build` with the iterable

### Example

```python

import csv
from pathlib import Path

from shapely import Point

from starplot import Star
from starplot.data.catalogs import Catalog

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "temp"


def parse_int(value):
    return int(value) if value else None

def parse_float(value):
    return float(value) if value else None
    

def stars():
    with open(DATA_PATH / "hygdata_v42.csv", "r") as hygfile:
        reader = csv.DictReader(hygfile)

        for row in reader:
            ra = parse_float(row.get("ra")) * 15
            dec = parse_float(row.get("dec"))
            geometry = Point(ra, dec)

            if not geometry.is_valid or geometry.is_empty:
                continue

            yield Star(
                hip=parse_int(row.get("hip")),
                ra=ra,
                dec=parse_float(row.get("dec")),
                constellation_id=row.get("con").lower(),
                magnitude=parse_float(row.get("mag")),
                ra_mas_per_year=parse_float(row.get("pmra")) or 0,
                dec_mas_per_year=parse_float(row.get("pmdec")) or 0,
                bv=parse_float(row.get("ci")),
                geometry=Point(ra, dec),
                epoch_year=2000,
                bayer=row.get("bayer"),
                flamsteed=row.get("flamsteed"),
                name=row.get("proper"),
            )


Catalog.build(
    objects=stars(),
    path=DATA_PATH / "hyg.parquet",
    chunk_size=200_000,
    columns=[
        "hip",
        "ra",
        "dec",
        "magnitude",
        "bv",
        "ra_mas_per_year",
        "dec_mas_per_year",
        "constellation_id",
        "geometry",
        "ccdm",
        "epoch_year",
        "name",
        "bayer",
        "flamsteed",
    ],
    # partition_columns=['_constellation_id'],
    sorting_columns=["magnitude"],
    compression="snappy",
    row_group_size=100_000,
)


```


<br/><br/><br/>