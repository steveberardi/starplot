from functools import cache
from pathlib import Path

from ibis import _
from shapely import Polygon, MultiPolygon

from starplot.config import settings
from starplot.data import db
from starplot.data.catalogs import Catalog, SpatialQueryMethod, BIG_SKY_MAG11
from starplot.data.translations import language_name_column, LANGUAGE_NAME_COLUMNS


@cache
def table(
    con,
    catalog: Catalog | Path | str = BIG_SKY_MAG11,
    table_name="stars",
    language: str = "en-us",
):
    if isinstance(catalog, Catalog):
        stars = catalog._load(connection=con, table_name=table_name)
    else:
        stars = con.read_parquet(str(catalog), table_name=table_name)

    designation_columns = ["name", "bayer", "flamsteed"] + LANGUAGE_NAME_COLUMNS
    designation_columns_missing = {
        col for col in designation_columns if col not in stars.columns
    }

    if designation_columns_missing and "hip" in stars.columns:
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
    catalog: Catalog | Path | str,
    extent: Polygon | MultiPolygon = None,
    filters=None,
    sql=None,
):
    filters = filters or []
    con = db.connect()
    stars = table(con=con, catalog=catalog, language=settings.language)

    if (
        catalog.spatial_query_method == SpatialQueryMethod.HEALPIX.value
        and catalog.healpix_nside
        and extent is not None
    ):
        healpix_indices = catalog.healpix_ids_from_extent(extent)
        stars = stars.filter(stars.healpix_index.isin(healpix_indices))
        stars = con.create_table("stars_temp", obj=stars, temp=True, overwrite=True)

    stars = stars.mutate(
        geometry=_.geometry.cast("geometry"),  # cast WKB to geometry type
    )

    if extent:
        stars = stars.filter(stars.geometry.intersects(extent))

    if filters:
        stars = stars.filter(*filters)

    if sql:
        result = stars.alias("_").sql(sql).select("pk").execute()
        pks = result["pk"].to_list()
        stars = stars.filter(_.pk.isin(pks))

    return stars
