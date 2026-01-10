# Creating Catalogs

Creating a new catalog is usually a three-step process:

1. Creating a [Catalog][starplot.data.Catalog] instance
2. Creating a reader function that reads some source data and yields sky objects
3. Calling the catalog's `build` method with the iterable

The size of the catalog you want to build and how you expect to query it will affect how you structure and build the catalog. See more on this in the sections below.


---

## Important Details

- Every sky object in a catalog needs to have an integer `pk` defined, and this needs to be unique for each object in the catalog. Starplot currently does not enforce this uniqueness itself, so be sure to make this unique when building a catalog.


---

## Creating small catalogs (< 1M objects)

**Define sorting columns**

When building a catalog you can optionally specify a list of `sorting_columns`. The catalog file(s) will be sorted by the fields in this list. If you plan on querying a catalog on a specific field frequently and that field has a medium or high standard deviation then you can improve query performance by sorting on that field. This will help the data backend scan data quickly.

**Examples**

- [Big Sky Star Catalog Builder](https://github.com/steveberardi/starplot-bigsky)
- [HYG Star Catalog Builder](https://github.com/steveberardi/starplot-hyg)
- [Constellations Catalog Builder](https://github.com/steveberardi/starplot-constellations)
- [OpenNGC DSO Catalog Builder](https://github.com/steveberardi/starplot-ongc)
- [HyperLeda Galaxy Catalog Builder](https://github.com/steveberardi/starplot-hyperleda)

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



<br/><br/><br/>


