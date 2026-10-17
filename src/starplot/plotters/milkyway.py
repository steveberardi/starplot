from ibis import _
from shapely import MultiPolygon, box, union_all

from starplot.constants import EDGE_BUFFER
from starplot.data import db
from starplot.data.catalogs import MILKY_WAY, Catalog
from starplot.models.milky_way import from_tuple
from starplot.profile import profile
from starplot.styles import PolygonStyle
from starplot.styles.helpers import use_style


class MilkyWayPlotterMixin:
    @profile
    @use_style(PolygonStyle, "milky_way")
    def milky_way(
        self,
        style: PolygonStyle = None,
        catalog: Catalog = MILKY_WAY,
        gid: str = "milky-way",
    ):
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
        df = mw.filter(_.geometry.intersects(extent)).order_by("pk").to_pandas()

        milky_ways = [from_tuple(m) for m in df.itertuples()]
        polygons = [m.geometry for m in milky_ways]
        mw_union = union_all(polygons)

        if isinstance(mw_union, MultiPolygon):
            polygons = mw_union.geoms
        else:
            polygons = [mw_union]

        with self.canvas.group(gid=gid):
            for p in polygons:
                # vertices at exactly RA 0 or 360 project to the opposite edge from their neighbors (creating
                # jumps in the polygon), so keep everything just inside the seam
                bounds = box(
                    EDGE_BUFFER, self.dec_min - 5, 360 - EDGE_BUFFER, self.dec_max + 5
                )
                p = p.intersection(bounds)

                if isinstance(p, MultiPolygon):
                    for pp in p.geoms:
                        self.polygon(
                            geometry=pp,
                            style=style,
                        )
                else:
                    self.polygon(
                        geometry=p,
                        style=style,
                    )
