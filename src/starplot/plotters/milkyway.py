from shapely.ops import unary_union

from starplot.data import db
from starplot.styles import PolygonStyle
from starplot.styles.helpers import use_style
from starplot.geometry import unwrap_polygon_360
from starplot.profile import profile


class MilkyWayPlotterMixin:
    @profile
    @use_style(PolygonStyle, "milky_way")
    def milky_way(self, style: PolygonStyle = None):
        """
        Plots the Milky Way

        Args:
            style: Styling of the Milky Way. If None, then the plot's style (specified when creating the plot) will be used
        """
        con = db.connect()
        mw = con.table("milky_way")

        extent = self._extent_mask()
        result = mw.filter(mw.geometry.intersects(extent)).to_pandas()

        mw_union = unary_union(
            [unwrap_polygon_360(row.geometry) for row in result.itertuples()]
        )

        if mw_union.geom_type == "MultiPolygon":
            polygons = mw_union.geoms
        else:
            polygons = [mw_union]

        for p in polygons:
            self.polygon(
                geometry=p,
                style=style,
            )
