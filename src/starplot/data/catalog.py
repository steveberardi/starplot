import yaml

from pathlib import Path
from collections.abc import Iterable

from shapely import wkb

import pandas as pd
import geopandas as gpd
import pyarrow as pa
import pyarrow.parquet as pq

"""
Ideas:

    StarCatalog.build(data, filename="stars.parquet", chunk_size=100_000)

    - also create some "index" file? with metadata: healpix nside, name, fields, etc

        gaia = StarCatalog.load(PATH / "catalog.yml")
        p.stars(where=[], catalog=gaia)

"""


def to_parquet(
    data: list[dict],
    path: str | Path,
    columns: list[str] = None,
    partition_columns: list[str] = None,
    sorting_columns: list[str] = None,
    compression: str = "snappy",
    row_group_size: int = 100_000,
) -> None:

    df = gpd.GeoDataFrame(data, crs="EPSG:4326")
    df = df.sort_values(sorting_columns)
    df = df[df.geometry.notna()]

    df["geometry"] = df["geometry"].apply(lambda x: x.wkb)

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
        path,
        compression=compression,
        row_group_size=row_group_size,
        sorting_columns=sort_columns,
    )

    df = pd.read_parquet(path)
    df["geometry"] = df["geometry"].apply(wkb.loads)
    gdf = gpd.GeoDataFrame(df, geometry="geometry")

    # gdf = gpd.read_parquet(path / "out.parquet")

    print(gdf)


def build(
    data: Iterable[object],
    path: str | Path,
    chunk_size: int = 100_000,
    columns: list[str] = None,
    partition_columns: list[str] = None,
    sorting_columns: list[str] = None,
    compression: str = "snappy",
    row_group_size: int = 100_000,
) -> None:
    columns = columns or []
    partition_columns = partition_columns or []
    sorting_columns = sorting_columns or []

    rows = []

    for row in data:
        rows.append({column: getattr(row, column) for column in columns})

        if len(rows) == chunk_size:
            to_parquet(
                data=rows,
                path=path,
                columns=columns,
                partition_columns=partition_columns,
                sorting_columns=sorting_columns,
                compression=compression,
                row_group_size=row_group_size,
            )
            rows = []

    if rows:
        to_parquet(
            data=rows,
            path=path,
            columns=columns,
            partition_columns=partition_columns,
            sorting_columns=sorting_columns,
            compression=compression,
            row_group_size=row_group_size,
        )


def write_catalog_file(
    path: str | Path,
    name: str,
    healpix_nside: int,
    extra_fields: list[str],
):
    data = dict(
        name=name,
        healpix_nside=healpix_nside,
        extra_fields=extra_fields,
    )

    with open(path, "w") as outfile:
        data_yaml = yaml.dump(data)
        outfile.write(data_yaml)
