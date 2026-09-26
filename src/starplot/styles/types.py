from typing import Annotated, Literal

from pydantic import AfterValidator
from pydantic.functional_serializers import PlainSerializer
from pydantic_extra_types.color import Color as _Color

Color = Annotated[
    _Color,
    PlainSerializer(
        lambda c: c.as_hex() if c and c != "none" else None,
        return_type=str,
    ),
]

MarkerSymbol = Literal[
    "plus",
    "circle",
    "square",
    "star",
    "diamond",
    "triangle",
    "circle_cross",
    "circle_crosshair",
    "circle_line",
    "comet",
    "star_4",
    "star_8",
    "ellipse",
    "satellite",
]


def _validate_stops(stops: list[tuple[float, str]]) -> list[tuple[float, str]]:
    if not stops:
        raise ValueError("gradient must have at least one stop")
    if stops[-1][0] != 1.0:
        raise ValueError("the last stop should always be at 1.0")
    return stops


GradientStops = Annotated[
    list[tuple[float, Color]],
    AfterValidator(_validate_stops),
    PlainSerializer(
        lambda stops: [(offset, c.as_hex() if c else None) for offset, c in stops],
        return_type=list,
    ),
]
