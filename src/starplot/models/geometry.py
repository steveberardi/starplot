from typing import Union

from shapely.geometry import Point, Polygon, MultiPolygon

from starplot import geod, utils


def circle(center, diameter_degrees):
    points = geod.ellipse(
        center,
        diameter_degrees,
        diameter_degrees,
        angle=0,
        num_pts=100,
    )
    points = [
        (round(24 - utils.lon_to_ra(lon), 4), round(dec, 4)) for lon, dec in points
    ]
    return Polygon(points)


def to_24h(geometry: Union[Point, Polygon, MultiPolygon]):
    def _to_poly24(p: Polygon):
        coords = list(zip(*p.exterior.coords.xy))
        coords = [(round(lon / 15, 4), round(dec, 4)) for lon, dec in coords]
        return Polygon(coords)

    def _to_point24(p: Point):
        return Point(round(p.x / 15, 4), round(p.y, 4))

    geometry_type = str(geometry.geom_type)

    if geometry_type == "MultiPolygon":
        polygons = []
        for p in geometry.geoms:
            p24 = _to_poly24(p)
            polygons.append(p24)
        return MultiPolygon(polygons)
    elif geometry_type == "Polygon":
        return _to_poly24(geometry)
    elif geometry_type == "Point":
        return _to_point24(geometry)
    else:
        raise ValueError(f"Unsupported geometry type: {geometry_type}")
