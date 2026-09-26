from functools import cache

from shapely import MultiPolygon, Polygon


class ExtentMaskMixin:
    @cache
    def _extent_mask(self):
        """
        Returns shapely geometry objects of extent (RA = 0...360)

        If the extent crosses equinox, then a MultiPolygon will be returned
        """
        if self._is_global_extent():
            return Polygon(
                [
                    (0, -90),
                    (360, -90),
                    (360, 90),
                    (0, 90),
                    (0, -90),
                ]
            )

        ra_min = self.ra_min
        ra_max = self.ra_max
        dec_min = self.dec_min
        dec_max = self.dec_max

        if ra_max <= 360:
            coords = [
                [ra_min, dec_min],
                [ra_max, dec_min],
                [ra_max, dec_max],
                [ra_min, dec_max],
                [ra_min, dec_min],
            ]
            return Polygon(coords)

        else:
            coords_1 = [
                [ra_min, dec_min],
                [360, dec_min],
                [360, dec_max],
                [ra_min, dec_max],
                [ra_min, dec_min],
            ]
            coords_2 = [
                [0, dec_min],
                [(ra_max - 360), dec_min],
                [(ra_max - 360), dec_max],
                [0, dec_max],
                [0, dec_min],
            ]

            return MultiPolygon(
                [
                    Polygon(coords_1),
                    Polygon(coords_2),
                ]
            )

    def _is_global_extent(self):
        """Returns True if the plot's RA/DEC range is the entire celestial sphere"""
        return all(
            [
                self.ra_min == 0,
                self.ra_max == 360,
                self.dec_min == -90,
                self.dec_max == 90,
            ]
        )


class CreateMapMixin:
    def create_map(self, height_degrees: float, width_degrees: float, *args, **kwargs):
        """
        Creates a map plot with this object at the center

        Args:
            height_degrees: Height of the map (degrees)
            width_degrees: Width of the map (degrees)
            *args: args passed through to [`MapPlot()`][starplot.MapPlot]
            **kwargs: kwargs passed through to [`MapPlot()`][starplot.MapPlot]

        Returns:
            MapPlot: new instance of a [`MapPlot`][starplot.MapPlot]
        """
        from starplot import MapPlot, geometry

        extent = geometry.rectangle(
            center=(self.ra, self.dec),
            height_degrees=height_degrees,
            width_degrees=width_degrees,
        )
        minx, miny, maxx, maxy = extent.bounds
        ra_min = minx
        ra_max = maxx
        dec_min = miny
        dec_max = maxy

        # handle wrapping
        if ra_max < ra_min:
            ra_max += 360

        p = MapPlot(
            ra_min=ra_min,
            ra_max=ra_max,
            dec_min=dec_min,
            dec_max=dec_max,
            *args,  # noqa B026
            **kwargs,
        )
        return p


class CreateOpticMixin:
    def create_optic(self, *args, **kwargs):
        """
        Creates an optic plot with this object at the center

        Args:
            *args: args passed through to [`OpticPlot()`][starplot.OpticPlot]
            **kwargs: kwargs passed through to [`OpticPlot()`][starplot.OpticPlot]

        Returns:
            OpticPlot: new instance of a [`OpticPlot`][starplot.OpticPlot]
        """
        from starplot import OpticPlot

        return OpticPlot(
            ra=self.ra,
            dec=self.dec,
            *args,  # noqa B026
            **kwargs,
        )
