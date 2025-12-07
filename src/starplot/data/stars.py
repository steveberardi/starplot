from functools import cache
from pathlib import Path

from ibis import _, row_number
from starplot.config import settings
from starplot.data import bigsky, DataFiles, db
from starplot.data.catalog import Catalog
from starplot.data.translations import language_name_column


class StarCatalog:
    """Built-in star catalogs"""

    BIG_SKY_MAG9 = "big-sky-mag9"

    """
    [Big Sky Catalog](https://github.com/steveberardi/bigsky) ~ 136,125 stars with limiting magnitude 9
    
    This is an _abridged_ version of the Big Sky Catalog.

    This catalog is included with Starplot, so does not require downloading any files.
    """

    BIG_SKY = "big-sky"
    """
    [Big Sky Catalog](https://github.com/steveberardi/bigsky) ~ 2.5M stars

    This is the full version of the Big Sky Catalog, which includes 2,557,500 stars from Hipparcos, Tycho-1, and Tycho-2.

    This catalog is very large (approx 100 MB), so it's not built-in to Starplot. When you plot stars and specify this catalog, the catalog 
    will be downloaded from the [Big Sky GitHub repository](https://github.com/steveberardi/bigsky) and saved to Starplot's data library 
    directory. You can override this download path with the environment variable `STARPLOT_DOWNLOAD_PATH`
    
    """


@cache
def table(
    catalog: StarCatalog | Catalog | Path | str = StarCatalog.BIG_SKY_MAG9,
    table_name="stars",
    language: str = "en-us",
):
    con = db.connect()

    if catalog == StarCatalog.BIG_SKY_MAG9:
        stars = con.read_parquet(DataFiles.BIG_SKY_MAG9, table_name=table_name)
    elif catalog == StarCatalog.BIG_SKY:
        bigsky.download_if_not_exists()
        stars = con.read_parquet(DataFiles.BIG_SKY, table_name=table_name)
    elif isinstance(catalog, Catalog):
        stars = con.read_parquet(str(catalog.path), table_name=table_name)
    else:
        stars = con.read_parquet(str(catalog), table_name=table_name)

    stars = stars.mutate(
        geometry=_.geometry.cast("geometry"),  # cast WKB to geometry type
        rowid=row_number(),
        sk=row_number(),
    )

    designation_columns_missing = {
        col for col in ["name", "bayer", "flamsteed"] if col not in stars.columns
    }

    if designation_columns_missing:
        designations = con.table("star_designations")
        designations = designations.mutate(
            name=getattr(designations, language_name_column(language))
        )
        stars_joined = stars.join(
            designations,
            stars.hip == designations.hip,
            how="left",
        )
        stars = stars_joined.select(*stars.columns, *designation_columns_missing)

    return stars


def load(
    extent=None,
    catalog: StarCatalog | Catalog | Path | str = StarCatalog.BIG_SKY_MAG9,
    filters=None,
    sql=None,
):
    filters = filters or []
    stars = table(catalog, language=settings.language)

    if extent:
        stars = stars.filter(stars.geometry.intersects(extent))

    if filters:
        stars = stars.filter(*filters)

    if sql:
        result = stars.alias("_").sql(sql).select("sk").execute()
        skids = result["sk"].to_list()
        stars = stars.filter(_.sk.isin(skids))

    return stars
