from functools import cache

from ibis import _, row_number

from starplot.config import settings
from starplot.data import db
from starplot.data.translations import language_name_column


@cache
def table(language):
    con = db.connect()
    c = con.table("constellations")

    return c.mutate(
        ra=_.center_ra,
        dec=_.center_dec,
        constellation_id=_.iau_id,
        boundary=_.geometry,
        name=getattr(c, language_name_column(language)),
        rowid=row_number(),
        sk=row_number(),
    )


def load(extent=None, filters=None, sql=None):
    filters = filters or []
    c = table(language=settings.language)

    if extent:
        filters.append(_.geometry.intersects(extent))

    if filters:
        c = c.filter(*filters)

    if sql:
        result = c.alias("_").sql(sql).select("sk").execute()
        skids = result["sk"].to_list()
        c = c.filter(_.sk.isin(skids))

    return c


def load_borders(extent=None, filters=None):
    filters = filters or []
    con = db.connect()
    c = con.table("constellation_borders")
    c = c.mutate(
        # ra=_.center_ra,
        # dec=_.center_dec,
        # constellation_id=_.iau_id,
        rowid=row_number(),
        # boundary=_.geometry,
    )

    if extent:
        filters.append(_.geometry.intersects(extent))

    if filters:
        return c.filter(*filters)

    return c
