from pathlib import Path
from collections.abc import Iterable

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# from starplot.models import Star


"""
Ideas:

    StarCatalog.build(data, filename="stars.parquet", chunk_size=100_000)

    - also create some "index" file? with metadata: healpix nside, name, fields, etc

        gaia = StarCatalog.load(PATH / "catalog.yml")
        p.stars(where=[], catalog=gaia)

"""

def create_star_catalog(
    data: Iterable["Star"],
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

    for star in data:
        rows.append({column: getattr(star, column) for column in columns})

        if len(rows) == chunk_size:
            to_parquet(
                data=rows,
                path=path,
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
            partition_columns=partition_columns,
            sorting_columns=sorting_columns,
            compression=compression,
            row_group_size=row_group_size,
        )


def to_parquet(
    data: list[dict], 
    path: str | Path,
    columns: list[str] = None,
    partition_columns: list[str] = None,
    sorting_columns: list[str] = None,
    compression: str = "snappy",
    row_group_size: int = 100_000,
) -> None:


    df = pd.DataFrame.from_records(data)
    df = df.sort_values(sorting_columns)
    
    table = pa.Table.from_pandas(df)

    sort_columns = [
        pq.SortingColumn(columns.index(c)) for c in sorting_columns
    ]

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
        path / "out.parquet",
        compression=compression,
        row_group_size=row_group_size,
        sorting_columns=sort_columns,
    )
