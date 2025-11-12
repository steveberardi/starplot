from functools import cache

from ibis import _, row_number, coalesce

from starplot.config import settings
from starplot.data import db
from starplot.data.translations import language_name_column


@cache
def table(language):
    con = db.connect()
    dsos = con.table("deep_sky_objects")

    return dsos.mutate(
        ra=_.ra_degrees,
        dec=_.dec_degrees,
        constellation_id=_.constellation,
        magnitude=coalesce(_.mag_v, _.mag_b, None),
        size=_.size_deg2,
        common_names=getattr(
            dsos, language_name_column(language, column_prefix="common_names")
        ),
        rowid=row_number(),
        sk=row_number(),
    )


def load(extent=None, filters=None, sql=None):
    filters = filters or []
    dsos = table(language=settings.language)

    if extent:
        dsos = dsos.filter(_.geometry.intersects(extent))

    filters.extend([_.ra_degrees.notnull() & _.dec_degrees.notnull()])

    if filters:
        dsos = dsos.filter(*filters)

    if sql:
        result = dsos.alias("_").sql(sql).select("sk").execute()
        skids = result["sk"].to_list()
        dsos = dsos.filter(_.sk.isin(skids))

    return dsos
