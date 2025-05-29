import json

from functools import cache
from typing import Optional

from shapely import to_geojson, from_geojson, Geometry
from shapely.geometry import Polygon, MultiPolygon, Point

from pydantic_core import core_schema

from pydantic import (
    BaseModel,
    computed_field,
)
from skyfield.api import position_of_radec, load_constellation_map

from starplot.mixins import CreateMapMixin, CreateOpticMixin


class ShapelyPydantic:
    @classmethod
    def validate(cls, field_value, info):
        return field_value.is_valid

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler) -> core_schema.CoreSchema:
        def validate_from_geojson(value: dict) -> Geometry:
            return from_geojson(json.loads(value))

        from_dict_schema = core_schema.chain_schema(
            [
                core_schema.dict_schema(),
                core_schema.no_info_plain_validator_function(validate_from_geojson),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_dict_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(Geometry),
                    from_dict_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: json.loads(to_geojson(instance))
            ),
        )


class ShapelyPolygon(ShapelyPydantic, Polygon):
    pass


class ShapelyMultiPolygon(ShapelyPydantic, MultiPolygon):
    pass


class ShapelyPoint(ShapelyPydantic, Point):
    pass


@cache
def constellation_at():
    return load_constellation_map()


class SkyObject(BaseModel, CreateMapMixin, CreateOpticMixin):
    """
    Basic sky object model.
    """

    ra: float
    """Right Ascension, in degrees (0 to 360)"""

    dec: float
    """Declination, in degrees (-90 to 90)"""

    _constellation_id: Optional[str] = None

    @computed_field
    @property
    def constellation_id(self) -> str | None:
        """Identifier of the constellation that contains this object. The ID is the three-letter (all lowercase) abbreviation from the International Astronomical Union (IAU)."""
        if not self._constellation_id:
            pos = position_of_radec(self.ra, self.dec)
            self._constellation_id = constellation_at()(pos).lower()
        return self._constellation_id

    def constellation(self):
        """Returns an instance of the [`Constellation`][starplot.models.Constellation] that contains this object"""
        from starplot.models import Constellation

        return Constellation.get(iau_id=self.constellation_id)
