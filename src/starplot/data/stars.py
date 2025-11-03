from functools import cache

from ibis import _, row_number

from starplot.config import settings
from starplot.data import bigsky, DataFiles, db
from starplot.data.translations import language_name_column


class StarCatalog:
    """Built-in star catalogs"""

    BIG_SKY_MAG11 = "big-sky-mag11"
    """
    [Big Sky Catalog](https://github.com/steveberardi/bigsky) ~ 370k stars up to magnitude 10
    
    This is an _abridged_ version of the Big Sky Catalog, including stars up to a limiting magnitude of 10 (total = 368,330 981,852).

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
    catalog: StarCatalog = StarCatalog.BIG_SKY_MAG11,
    table_name="stars",
    language: str = "en-us",
):
    con = db.connect()

    if catalog == StarCatalog.BIG_SKY_MAG11:
        stars = con.read_parquet(DataFiles.BIG_SKY_MAG11, table_name=table_name)
    elif catalog == StarCatalog.BIG_SKY:
        bigsky.download_if_not_exists()
        stars = con.read_parquet(DataFiles.BIG_SKY, table_name=table_name)
    else:
        raise ValueError("Unrecognized star catalog.")

    designations = con.table("star_designations")

    stars = stars.mutate(
        epoch_year=2000,
        ra=_.ra_degrees,
        dec=_.dec_degrees,
        constellation_id=_.constellation,
        ra_hours=_.ra_degrees / 15,
        # stars parquet does not have geometry field
        geometry=_.ra_degrees.point(_.dec_degrees),
        rowid=row_number(),
        sk=row_number(),
    )

    designations = designations.mutate(
        name=getattr(designations, language_name_column(language))
    )

    stars = stars.join(
        designations,
        [
            stars.hip == designations.hip,
            (stars.ccdm.startswith("A")) | (stars.ccdm == "") | (stars.ccdm.isnull()),
        ],
        how="left",
    )

    return stars


def load(
    extent=None,
    catalog: StarCatalog = StarCatalog.BIG_SKY_MAG11,
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
