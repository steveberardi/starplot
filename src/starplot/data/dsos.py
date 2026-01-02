from functools import cache
from pathlib import Path

from ibis import _

from starplot.config import settings
from starplot.data import db
from starplot.data.catalogs import Catalog, SpatialQueryMethod
from starplot.data.translations import (
    language_name_column,
    LANGUAGES,
)


@cache
def table(
    con,
    catalog: Catalog | Path | str,
    language: str,
):
    table_name = "deep_sky_objects"

    if isinstance(catalog, Catalog):
        dsos = catalog._load(connection=con, table_name=table_name)
    else:
        dsos = con.read_parquet(str(catalog), table_name=table_name)

    name_column = language_name_column(language, column_prefix="common_names")
    name_columns = [
        language_name_column(lang, column_prefix="common_names") for lang in LANGUAGES
    ]
    name_columns_missing = {col for col in name_columns if col not in dsos.columns}

    if name_columns_missing and "name" in dsos.columns:
        dso_names = con.table("dso_names")
        dsos_joined = dsos.join(
            dso_names,
            dsos.name == dso_names.open_ngc_name,
            how="left",
        )
        dsos = dsos_joined.select(*dsos.columns, *name_columns_missing)

    if name_column not in dsos.columns:
        name_column = "name"

    return dsos.mutate(common_names=getattr(dsos, name_column))


def load(
    catalog: Catalog | Path | str,
    extent=None,
    filters=None,
    sql=None,
):
    filters = filters or []
    con = db.connect()
    dsos = table(con=con, catalog=catalog, language=settings.language)

    if (
        catalog.spatial_query_method == SpatialQueryMethod.HEALPIX.value
        and catalog.healpix_nside
        and extent is not None
    ):
        healpix_indices = catalog.healpix_ids_from_extent(extent)
        dsos = dsos.filter(dsos.healpix_index.isin(healpix_indices))
        dsos = con.create_table("dsos_temp", obj=dsos, temp=True, overwrite=True)

    dsos = dsos.mutate(
        geometry=_.geometry.cast("geometry"),  # cast WKB to geometry type
    )

    if extent:
        dsos = dsos.filter(_.geometry.intersects(extent))

    filters.extend([_.ra.notnull() & _.dec.notnull()])

    if filters:
        dsos = dsos.filter(*filters)

    if sql:
        result = dsos.alias("_").sql(sql).select("pk").execute()
        pks = result["pk"].to_list()
        dsos = dsos.filter(_.pk.isin(pks))

    return dsos
