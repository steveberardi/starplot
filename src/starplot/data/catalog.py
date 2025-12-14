from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from shapely import Geometry

from starplot.models.base import SkyObject


def to_parquet(
    rows: list[dict],
    path: Path,
    columns: list[str] = None,
    partition_columns: list[str] = None,
    sorting_columns: list[str] = None,
    compression: str = "snappy",
    row_group_size: int = 100_000,
    chunk_id: int = 0,
) -> None:
    import pandas as pd

    # import geopandas as gpd
    import pyarrow as pa
    import pyarrow.parquet as pq

    # GeoDataFrame not needed cause we convert to WKB?
    # df = gpd.GeoDataFrame(rows, crs="EPSG:4326")
    # df = df[df.geometry.notna()]
    # df["geometry"] = df["geometry"].apply(lambda x: x.wkb)

    df = pd.DataFrame(rows)
    df = df.sort_values(sorting_columns)

    table = pa.Table.from_pandas(df)
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
        path.with_stem(f"{path.stem}_{chunk_id}"),
        compression=compression,
        row_group_size=row_group_size,
        sorting_columns=sort_columns,
    )

    # df = pd.read_parquet(path)
    # df["geometry"] = df["geometry"].apply(wkb.loads)
    # gdf = gpd.GeoDataFrame(df, geometry="geometry")
    # print(gdf)


@dataclass(frozen=True)
class Catalog:
    """Catalog of objects"""

    path: Path
    """Path of the catalog"""

    hive_partitioning: bool = False
    """If the catalog uses hive partitioning, then set this to True"""

    healpix_nside: int = None
    """HEALPix resolution (NSIDE)"""

    @classmethod
    def build(
        cls,
        objects: Iterable[SkyObject],
        path: str | Path,
        chunk_size: int = 1_000_000,
        columns: list[str] = None,
        partition_columns: list[str] = None,
        sorting_columns: list[str] = None,
        compression: str = "snappy",
        row_group_size: int = 200_000,
    ) -> None:
        """
        Creates a custom catalog of sky objects. Output is one or more Parquet files.

        Args:
            objects: Iterable that contains the sky objects for the catalog
            path: Output path of the catalog
            chunk_size: Max number of objects to write per file
            columns: List of columns to include in the catalog
            partition_columns: List of columns to create Hive partitions for
            sorting_columns: List of columns to sort by
            compression: Type of compression to use
            row_group_size: Row group size for the catalog parquet file


        TODO :

            - Add healpix
            - Only allow paths? Use UUID as filename? That works better with chunking

        """

        if not isinstance(path, Path):
            path = Path(path)

        if partition_columns and not path.is_dir():
            raise ValueError("Path must be a directory when using partition columns.")

        chunk_ctr = 0
        columns = columns or []
        partition_columns = partition_columns or []
        sorting_columns = sorting_columns or []

        rows = []

        def serialize(obj):
            """Converts geometry types to WKB"""
            return obj.wkb if isinstance(obj, Geometry) else obj

        for row in objects:
            rows.append({column: serialize(getattr(row, column)) for column in columns})

            if len(rows) == chunk_size:
                to_parquet(
                    rows=rows,
                    path=path,
                    columns=columns,
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
                partition_columns=partition_columns,
                sorting_columns=sorting_columns,
                compression=compression,
                row_group_size=row_group_size,
                chunk_id=chunk_ctr,
            )
