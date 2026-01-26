import glob
from enum import Enum

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from astropy import units as u
from astropy_healpix import HEALPix
from ibis import Table
import pyarrow as pa
from shapely import Geometry, Polygon, MultiPolygon

from starplot.config import settings
from starplot.models.base import SkyObject
from starplot.data.utils import download


def merge_schemas(df, explicit_schema: pa.Schema) -> pa.Schema:
    """Merge explicit schema with inferred schema for remaining columns."""
    df_columns = df.columns.tolist()

    explicit_cols = {field.name for field in explicit_schema}

    # infer schema for ALL columns
    inferred_table = pa.Table.from_pandas(df)
    inferred_schema = inferred_table.schema

    # add explicit fields first
    fields = [f for f in explicit_schema if f.name in df_columns]

    # add inferred fields for remaining columns
    for field in inferred_schema:
        if field.name not in explicit_cols:
            fields.append(field)

    return pa.schema(fields)


def to_parquet(
    rows: list[dict],
    path: Path,
    columns: list[str] = None,
    schema: pa.Schema = None,
    partition_columns: list[str] = None,
    sorting_columns: list[str] = None,
    compression: str = "snappy",
    row_group_size: int = 100_000,
    chunk_id: int = 0,
) -> None:
    import pandas as pd
    import pyarrow.parquet as pq

    df = pd.DataFrame(rows)
    df = df.sort_values(sorting_columns)

    merged_schema = merge_schemas(df, schema)
    table = pa.Table.from_pandas(df, schema=merged_schema)

    if "__index_level_0__" in table.column_names:
        table = table.drop_columns("__index_level_0__")

    sort_columns = [pq.SortingColumn(columns.index(c)) for c in sorting_columns]

    if partition_columns:
        pq.write_to_dataset(
            table,
            root_path=path,
            partition_cols=partition_columns,
            compression=compression,
            row_group_size=row_group_size,
            sorting_columns=sort_columns,
        )
        return

    pq.write_table(
        table,
        path if chunk_id is None else path.with_stem(f"{path.stem}_{chunk_id}"),
        compression=compression,
        row_group_size=row_group_size,
        sorting_columns=sort_columns,
    )
    # schema = pq.read_schema(filename)
    # print("\nColumn names:", schema.names)
    # print("Column types:", schema.types)
    # print(schema.to_string())

    # parquet_file = pq.ParquetFile(filename)
    # print(f"Parquet file: {filename} Schema")
    # print(parquet_file.schema)

    # print("\nFull Metadata:")
    # print(parquet_file.metadata)

    # df = pd.read_parquet(path)
    # df["geometry"] = df["geometry"].apply(wkb.loads)
    # gdf = gpd.GeoDataFrame(df, geometry="geometry")
    # print(gdf)


class SpatialQueryMethod(Enum):
    """Options for spatial querying method"""

    GEOMETRY = "geometry"
    """Use the `geometry` field"""

    HEALPIX = "healpix"
    """Use the `healpix_index` field"""


@dataclass
class Catalog:
    """Catalog of objects"""

    path: Path | str
    """Path of the catalog. If using Hive partitions, this should be a glob (e.g. `/data/**/*.parquet`)."""

    url: str = None
    """Remote URL of the catalog. If the catalog doesn't exist at the `path` then it'll be downloaded from this URL."""

    hive_partitioning: bool = False
    """If the catalog uses hive partitioning, then set this to True"""

    healpix_nside: int = None
    """HEALPix resolution (NSIDE)"""

    spatial_query_method: SpatialQueryMethod = SpatialQueryMethod.GEOMETRY
    """
    Method to use for spatial querying on this catalog. 

    For relatively small catalogs (less than 1 million objects), the geometry method should have good performance.
    
    For larger catalogs, you can improve querying performance tremendously by defining a `healpix_nside` on the catalog,
    and setting this query method to `SpatialQueryMethod.HEALPIX`
    """

    _healpix: HEALPix = None

    def __post_init__(self):
        if not isinstance(self.path, Path):
            self.path = Path(self.path)
        if self.healpix_nside is not None:
            self._healpix = HEALPix(nside=self.healpix_nside, order="nested")

    def __eq__(self, other):
        if isinstance(other, Catalog):
            return str(self.path) == str(other.path)
        return NotImplemented

    def __hash__(self):
        return hash(str(self.path))

    def exists(self) -> bool:
        """Returns true if the catalog path exists, else False."""
        return any(glob.iglob(str(self.path)))

    def download(self, silent: bool = False):
        """Downloads the catalog from its URL to its path"""
        download(
            url=self.url,
            download_path=self.path,
            description=f"Catalog: {self.url}",
            silent=silent,
        )

    def download_if_not_exists(self, silent: bool = False):
        """Downloads the catalog only if it doesn't already exist at its path"""
        if not self.exists() and self.url:
            self.download(silent=silent)

    def healpix_ids_from_extent(self, extent: Polygon | MultiPolygon) -> list[int]:
        """
        Returns HEALPix ids from a given polygon or multipolygon

        Args:
            extent: Polygon or multipolygon to get the HEALPix ids for

        Returns:
            List of integer HEALPix ids that are in the geometry (inclusive)
        """
        healpix_ids = set()
        polygons = extent.geoms if isinstance(extent, MultiPolygon) else [extent]

        for p in polygons:
            minx, miny, maxx, maxy = p.bounds
            radius = max(abs(maxx - minx), abs(maxy - miny))
            healpix_ids.update(
                [
                    int(i)
                    for i in self._healpix.cone_search_lonlat(
                        lon=p.centroid.x * u.deg,
                        lat=p.centroid.y * u.deg,
                        radius=radius * u.deg,
                    )
                ]
            )
        return healpix_ids

    def _load(self, connection, table_name) -> Table:
        self.download_if_not_exists()
        return connection.read_parquet(
            str(self.path),
            table_name=table_name,
            hive_partitioning=self.hive_partitioning,
        )

    def build(
        self,
        objects: Iterable[SkyObject],
        chunk_size: int = 1_000_000,
        columns: list[str] = None,
        partition_columns: list[str] = None,
        sorting_columns: list[str] = None,
        compression: str = "snappy",
        row_group_size: int = 200_000,
    ) -> None:
        """
        Creates the catalog from an iterable of sky objects. Output is one or more Parquet files.

        Args:
            objects: Iterable that contains the sky objects for the catalog
            chunk_size: Max number of objects to write per file
            columns: List of columns to include in the catalog. Only the columns in this list will be written to the Parquet files.
            partition_columns: List of columns to create Hive partitions for
            sorting_columns: List of columns to sort by
            compression: Type of compression to use -- this is passed directly to PyArrow's Parquet writer.
            row_group_size: Row group size for the Parquet files
        """
        path = self.path
        if partition_columns:
            path.mkdir(parents=True, exist_ok=True)

        chunk_ctr = 0
        schema = None
        columns = columns or []
        partition_columns = partition_columns or []
        sorting_columns = sorting_columns or []
        rows = []

        hpix = None
        if self.healpix_nside is not None:
            hpix = HEALPix(nside=self.healpix_nside, order="nested")
            columns.append("healpix_index")

        def serialize(obj):
            """Converts geometry types to WKB"""
            return obj.wkb if isinstance(obj, Geometry) else obj

        for row in objects:
            if schema is None:
                schema = row._pyarrow_schema()

            if hpix:
                idx = hpix.lonlat_to_healpix([row.ra] * u.deg, [row.dec] * u.deg)
                row.healpix_index = idx[0]

            rows.append({column: serialize(getattr(row, column)) for column in columns})

            if len(rows) == chunk_size:
                to_parquet(
                    rows=rows,
                    path=path,
                    columns=columns,
                    schema=schema,
                    partition_columns=partition_columns,
                    sorting_columns=sorting_columns,
                    compression=compression,
                    row_group_size=row_group_size,
                    chunk_id=chunk_ctr,
                )
                rows = []
                chunk_ctr += 1

        if rows:
            to_parquet(
                rows=rows,
                path=path,
                columns=columns,
                schema=schema,
                partition_columns=partition_columns,
                sorting_columns=sorting_columns,
                compression=compression,
                row_group_size=row_group_size,
                chunk_id=chunk_ctr if chunk_ctr else None,
            )


# --------------------------------------------------------
#  Catalog definitions
# --------------------------------------------------------

BIG_SKY = Catalog(
    path=settings.data_path / "stars.bigksy.0.1.3.mag16.parquet",
    url="https://github.com/steveberardi/starplot-bigsky/releases/download/v0.1.3/stars.bigksy.0.1.3.mag16.parquet",
)
"""
[Big Sky Catalog](https://github.com/steveberardi/bigsky) ~ 2.5M stars

This is the full version of the Big Sky Catalog, which includes 2,557,501 stars from Hipparcos, Tycho-1, and Tycho-2.
"""

BIG_SKY_MAG11 = Catalog(
    path=settings.data_path / "stars.bigksy.0.1.3.mag11.parquet",
    url="https://github.com/steveberardi/starplot-bigsky/releases/download/v0.1.3/stars.bigksy.0.1.3.mag11.parquet",
)
"""
[Big Sky Catalog](https://github.com/steveberardi/bigsky) ~ 983,823 stars with limiting magnitude 11

This is an _abridged_ version of the Big Sky Catalog.
"""

BIG_SKY_MAG9 = Catalog(
    path=settings.data_path / "stars.bigksy.0.1.3.mag9.parquet",
    url="https://github.com/steveberardi/starplot-bigsky/releases/download/v0.1.3/stars.bigksy.0.1.3.mag9.parquet",
)
"""
[Big Sky Catalog](https://github.com/steveberardi/bigsky) ~ 136,126 stars with limiting magnitude 9

This is an _abridged_ version of the Big Sky Catalog.
"""

OPEN_NGC = Catalog(
    path=settings.data_path / "ongc.0.1.2.parquet",
    url="https://github.com/steveberardi/starplot-ongc/releases/download/v0.1.2/ongc.0.1.2.parquet",
)
"""
[OpenNGC](https://github.com/mattiaverga/OpenNGC) catalog, including nebulae outlines.
"""

CONSTELLATIONS_IAU = Catalog(
    path=settings.data_path / "constellations.0.3.3.parquet",
    url="https://github.com/steveberardi/starplot-constellations/releases/download/v0.3.3/constellations.0.3.3.parquet",
)
"""
Constellations recognized by IAU, with lines by Sky & Telescope.
"""

CONSTELLATION_BORDERS = Catalog(
    path=settings.data_path / "constellations-borders-0.3.1.parquet",
    url="https://github.com/steveberardi/starplot-constellations/releases/download/v0.3.1/constellations-borders.0.3.1.parquet",
)

MILKY_WAY = Catalog(
    path=settings.data_path / "milky_way-0.1.0.parquet",
    url="https://github.com/steveberardi/starplot-milkyway/releases/download/v0.1.0/milky_way.parquet",
)


def download_all_catalogs(silent=False):
    BIG_SKY.download_if_not_exists(silent=silent)
    BIG_SKY_MAG9.download_if_not_exists(silent=silent)
    BIG_SKY_MAG11.download_if_not_exists(silent=silent)
    OPEN_NGC.download_if_not_exists(silent=silent)
    CONSTELLATIONS_IAU.download_if_not_exists(silent=silent)
    CONSTELLATION_BORDERS.download_if_not_exists(silent=silent)
    MILKY_WAY.download_if_not_exists(silent=silent)
