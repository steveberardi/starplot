from shapely.ops import unary_union

from ibis import _

from starplot.data import db
from starplot.data.catalogs import Catalog, MILKY_WAY
from starplot.styles import PolygonStyle
from starplot.styles.helpers import use_style
from starplot.geometry import split_polygon_at_zero
from starplot.profile import profile
from starplot.models.milky_way import from_tuple


class MilkyWayPlotterMixin:
    @profile
    @use_style(PolygonStyle, "milky_way")
    def milky_way(self, style: PolygonStyle = None, catalog: Catalog = MILKY_WAY):
        """
        Plots the Milky Way

        Args:
            style: Styling of the Milky Way. If None, then the plot's style (specified when creating the plot) will be used
            catalog: Catalog to use for Milky Way polygons
        """
        con = db.connect()
        mw = catalog._load(connection=con, table_name="milky_way")
        mw = mw.mutate(
            geometry=_.geometry.cast("geometry"),  # cast WKB to geometry type
        )

        extent = self._extent_mask()
        df = mw.filter(_.geometry.intersects(extent)).to_pandas()

        milky_ways = [from_tuple(m) for m in df.itertuples()]

        polygons = []
        for milky_way in milky_ways:
            polygons.extend(split_polygon_at_zero(milky_way.geometry))

        mw_union = unary_union(polygons)

        if mw_union.geom_type == "MultiPolygon":
            polygons = mw_union.geoms
        else:
            polygons = [mw_union]

        for p in polygons:
            self.polygon(
                geometry=p.buffer(0.001),
                style=style,
            )
