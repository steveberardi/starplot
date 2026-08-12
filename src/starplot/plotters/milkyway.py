from ibis import _
from shapely import MultiPolygon, box, union_all

from starplot.data import db
from starplot.data.catalogs import MILKY_WAY, Catalog
from starplot.geometry import split_polygon_at_zero
from starplot.models.milky_way import from_tuple
from starplot.profile import profile
from starplot.styles import PolygonStyle
from starplot.styles.helpers import use_style


class MilkyWayPlotterMixin:
    @profile
    @use_style(PolygonStyle, "milky_way")
    def milky_way(self, style: PolygonStyle = None, catalog: Catalog = MILKY_WAY, gid: str = "milky-way"):
        """
        Plots the Milky Way

        Args:
            style: Styling of the Milky Way. If None, then the plot's style (specified when creating the plot) will be used
            catalog: Catalog to use for Milky Way polygons
            gid: Group id for this layer in the exported SVG
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

        mw_union = union_all(polygons)

        if isinstance(mw_union, MultiPolygon):
            polygons = mw_union.geoms
        else:
            polygons = [mw_union]

        with self.canvas.group(gid=gid):
            for p in polygons:
                bounds = box(0, self.dec_min - 5, 360, self.dec_max + 5)
                p = p.intersection(bounds)

                if isinstance(p, MultiPolygon):
                    for pp in p.geoms:
                        self.polygon(
                            geometry=pp.buffer(-0.001),
                            style=style,
                        )
                else:
                    self.polygon(
                        geometry=p.buffer(-0.001),
                        style=style,
                    )
