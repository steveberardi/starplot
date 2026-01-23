from dataclasses import dataclass

import pyarrow as pa
from shapely import Polygon, MultiPolygon

from starplot.models.base import SkyObject, CatalogObject


@dataclass(slots=True, kw_only=True)
class MilkyWay(CatalogObject, SkyObject):
    """
    Milky Way model.
    """

    geometry: Polygon | MultiPolygon
    """Shapely Polygon of the Milky Way's extent. Right ascension coordinates are in degrees (0...360)."""

    @classmethod
    def _pyarrow_schema(cls):
        base_schema = super(MilkyWay, cls)._pyarrow_schema()
        extra_fields = [
            pa.field("pk", pa.int64(), nullable=False),
            pa.field("geometry", pa.binary(), nullable=False),
        ]
        return pa.schema(list(base_schema) + extra_fields)


def from_tuple(d: tuple) -> MilkyWay:
    kwargs = {f: getattr(d, f) for f in MilkyWay._fields() if hasattr(d, f)}
    return MilkyWay(**kwargs)
