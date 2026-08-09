from typing import Annotated

from pydantic import AfterValidator
from pydantic.functional_serializers import PlainSerializer
from pydantic_extra_types.color import Color

ColorStr = Annotated[
    Color,
    PlainSerializer(
        lambda c: c.as_hex() if c and c != "none" else None,
        return_type=str,
    ),
]


def _validate_stops(stops: list[tuple[float, str]]) -> list[tuple[float, str]]:
    if not stops:
        raise ValueError("gradient must have at least one stop")
    if stops[-1][0] != 1.0:
        raise ValueError("the last stop should always be at 1.0")
    return stops


GradientStops = Annotated[
    list[tuple[float, ColorStr]],
    AfterValidator(_validate_stops),
    PlainSerializer(
        lambda stops: [(offset, c.as_hex() if c else None) for offset, c in stops],
        return_type=list,
    ),
]
