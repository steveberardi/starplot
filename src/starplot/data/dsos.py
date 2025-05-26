from functools import cache

import ibis
from ibis import _

from starplot.data import db


class DsoLabelMaker(dict):
    """
    This is pretty hacky, but it helps keep a consistent interface for plotting labels and any overrides.

    Basically this is just a dictionary that returns the key itself for any get() call, unless
    the key is present in the 'overrides' dict that's passed on init
    """

    def __init__(self, *args, **kwargs):
        self._overrides = kwargs.get("overrides") or {}

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key):
        return self._overrides.get(key) or key


DSO_LABELS_DEFAULT = DsoLabelMaker()


@cache
def table():
    con = db.connect()
    dsos = con.table("deep_sky_objects")

    return dsos.mutate(
        ra=_.ra_degrees,
        dec=_.dec_degrees,
        constellation_id=_.constellation,
        magnitude=ibis.coalesce(_.mag_v, _.mag_b, None),
        size=_.size_deg2,
        rowid=ibis.row_number(),
        sk=ibis.row_number(),
    )


def load(extent=None, filters=None, sql=None):
    filters = filters or []
    dsos = table()

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
