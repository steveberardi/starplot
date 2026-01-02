
# Creating Catalogs

Creating a new catalog is a two-step process:

1. Creating a reader that reads some source data and yields sky objects
2. Calling the class method `Catalog.build` with the iterable

---

## Creating small catalogs (< 1M objects)


**Define sorting columns**

When building a catalog you can optionally specify a list of `sorting_columns`. The catalog file(s) will be sorted by the fields in this list. If you plan on querying a catalog on a specific field frequently and that field has a medium or high standard deviation then you can improve query performance by sorting on that field. This will help the data backend scan data quickly.

**Examples**

- [Big Sky Star Catalog Builder](https://github.com/steveberardi/starplot-bigsky)
- [Constellations Catalog Builder](https://github.com/steveberardi/starplot-constellations)
- [OpenNGC DSO Catalog Builder](https://github.com/steveberardi/starplot-ongc)


---

## Creating large catalogs (1M+ objects)

When building very large catalogs, Starplot has a few options available for ensuring good performance on querying the catalog.

**Define Hive partition columns**

[Hive partitioning](https://duckdb.org/docs/stable/data/partitioning/hive_partitioning#hive-partitioning) is a way of grouping data into separate folders based on some value. For example, one way to group stars is by their constellation, so if you created a catalog of stars partitioned on `constellation_id` the resulting build path would contain a bunch of folders:

```
stars/
    constellation_id=and/
    constellation_id=cma/
    constellation_id=uma/
    ...
```

With these partition folders for constellations, queries for stars that reference the `constellation_id` will be much faster because the data backend (DuckDB in this case) only has to look in the relevant folders.

Hive partitions should only be created for fields that have low cardinality (i.e. a small number of unique values), because if the data has too many partitions that'll actually make querying slower.

Since most fields on Starplot models have high cardinality, the only fields that really make sense for Hive partitions are `constellation_id` or `healpix_index` -- and HEALPix is probably the best choice in most cases because that field can be used in spatial queries (more on this below).

**Define a HEALPix NSIDE**

[HEALPix](https://en.wikipedia.org/wiki/HEALPix) is an algorithm for dividing a sphere into equal-area sub-divisions, which are referred to as "pixels." It's commonly used for partitioning astronomical or geospatial data.

The NSIDE is the "resolution" of a HEALPix map for a dataset and determines the number of sub-divisions/pixels:

```
num_pixels = 12 * nside^2
```

So, an nside of 8 would result in 768 sub-divisions / pixels.

Starplot's catalog builder can automatically assign HEALPix values for objects (based on their RA/DEC) if you set the `healpix_nside` parameter on the `build` function. This will _only_ use the point coordinate of the object (RA/DEC), it will _not_ use the `geometry` field (so polygons are not currently supported).


**Set the spatial query method to HEALPix**

Starplot can perform spatial queries on catalogs by using the `geometry` field or the `healpix_index` field. When querying on the geometry field, Starplot has to first cast the geometry column from a WKB type to a geometry type which can significantly slow down the query on large catalogs, so if you're building a large catalog it's recommended to also set a HEALPix NSIDE, create a Hive partition for `healpix_index` and also set the spatial query method to "healpix".

**Large Catalog Checklist**

✅ Set sorting columns based on what you'll be querying on (e.g. magnitude)

✅ Define a HEALPix NSIDE that divides your data into chunks of 100 MB - 1 GB

✅ Set `healpix_index` as a partition column

✅ Set the spatial query method to HEALPix

✅ Combine Parquet files in each partition folder into a single file


**Examples**

- [Gaia DR3 Catalog Builder](https://github.com/steveberardi/starplot-gaia-dr3)


---


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


