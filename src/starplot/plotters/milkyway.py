from starplot.data import DataFiles
from starplot.styles import PolygonStyle
from starplot.styles.helpers import use_style
from starplot.utils import lon_to_ra


class MilkyWayPlotterMixin:
    @use_style(PolygonStyle, "milky_way")
    def milky_way(self, style: PolygonStyle = None):
        """
        Plots the Milky Way

        Args:
            style: Styling of the Milky Way. If None, then the plot's style (specified when creating the plot) will be used
        """

        mw = self._read_geo_package(DataFiles.MILKY_WAY.value)

        if mw.empty:
            return

        def _prepare_polygon(p):
            points = list(zip(*p.boundary.coords.xy))
            # convert lon to RA and reverse so the coordinates are counterclockwise order
            return [(lon_to_ra(lon) * 15, dec) for lon, dec in reversed(points)]

        # create union of all Milky Way patches
        gs = mw.geometry.to_crs(self._plate_carree)
        mw_union = gs.buffer(0.1).unary_union.buffer(-0.1)
        polygons = []

        if mw_union.geom_type == "MultiPolygon":
            polygons.extend([_prepare_polygon(polygon) for polygon in mw_union.geoms])
        else:
            polygons.append(_prepare_polygon(mw_union))

        for polygon_points in polygons:
            self._polygon(
                points=polygon_points,
                style=style,
            )
