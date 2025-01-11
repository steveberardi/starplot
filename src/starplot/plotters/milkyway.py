from shapely.ops import unary_union

from starplot.data import db
from starplot.styles import PolygonStyle
from starplot.styles.helpers import use_style
from starplot.geometry import unwrap_polygon_360
from starplot.profile import profile



from shapely.ops import transform

def round_coordinates(geom, ndigits=4):
    
   def _round_coords(x, y, z=None):
      x = round(x, ndigits)
      y = round(y, ndigits)

      if z is not None:
          z = round(x, ndigits)
          return (x,y,z)
      else:
          return (x,y)
   
   return transform(_round_coords, geom)

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

        # df = mw.to_pandas()
        
        # # df.geometry = shapely.set_precision(df.geometry, grid_size=0.0001)
        # df['geometry'] = df.geometry.apply(round_coordinates)

        # df.to_file(
        #     "temp/milkyway.json", driver="GeoJSON",
        # )

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
