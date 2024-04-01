from shapely import Polygon, MultiPolygon


class ExtentMaskMixin:
    def _extent_mask(self):
        """
        Returns shapely geometry objects of extent (RA = 0...360)

        If the extent crosses equinox, then two Polygons will be returned
        """
        if self.ra_max < 24:
            coords = [
                [self.ra_min * 15, self.dec_min],
                [self.ra_max * 15, self.dec_min],
                [self.ra_min * 15, self.dec_max],
                [self.ra_max * 15, self.dec_max],
            ]
            return Polygon(coords)

        else:
            coords_1 = [
                [self.ra_min * 15, self.dec_min],
                [360, self.dec_min],
                [self.ra_min * 15, self.dec_max],
                [360, self.dec_max],
            ]
            coords_2 = [
                [0, self.dec_min],
                [(self.ra_max - 24) * 15, self.dec_min],
                [0, self.dec_max],
                [(self.ra_max - 24) * 15, self.dec_max],
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
                self.ra_max == 24,
                self.dec_min == -90,
                self.dec_max == 90,
            ]
        )


class CreateMapMixin:
    def create_map(self, extent, *args, **kwargs):
        """
        Creates a map plot with this object at the center

        Args:
            extent: Extent of the map (height and width), in degrees
            *args: args passed through to [`MapPlot()`][starplot.MapPlot]
            **kwargs: kwargs passed through to [`MapPlot()`][starplot.MapPlot]

        Returns:
            MapPlot: new instance of a [`MapPlot`][starplot.MapPlot]
        """
        from starplot import MapPlot, geod

        ex = geod.rectangle(
            center=(self.ra, self.dec),
            height_degrees=extent,
            width_degrees=extent,
        )
        ra_min = ex[0][0] / 15
        ra_max = ex[2][0] / 15
        dec_min = ex[0][1]
        dec_max = ex[2][1]

        # handle wrapping
        if ra_max < ra_min:
            ra_max += 24

        p = MapPlot(
            ra_min=ra_min,
            ra_max=ra_max,
            dec_min=dec_min,
            dec_max=dec_max,
            *args,
            **kwargs,
        )
        return p


class CreateOpticMixin:
    def create_optic(self, extent, *args, **kwargs):
        pass
