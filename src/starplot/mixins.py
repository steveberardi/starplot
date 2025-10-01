from functools import cache

from shapely import Polygon, MultiPolygon
from starplot.profile import profile


class ExtentMaskMixin:
    @cache
    def _extent_mask(self):
        """
        Returns shapely geometry objects of extent (RA = 0...360)

        If the extent crosses equinox, then a MultiPolygon will be returned
        """
        if self.ra_max <= 360:
            coords = [
                [self.ra_min, self.dec_min],
                [self.ra_max, self.dec_min],
                [self.ra_max, self.dec_max],
                [self.ra_min, self.dec_max],
                [self.ra_min, self.dec_min],
            ]
            return Polygon(coords)

        else:
            coords_1 = [
                [self.ra_min, self.dec_min],
                [360, self.dec_min],
                [360, self.dec_max],
                [self.ra_min, self.dec_max],
                [self.ra_min, self.dec_min],
            ]
            coords_2 = [
                [0, self.dec_min],
                [(self.ra_max - 360), self.dec_min],
                [(self.ra_max - 360), self.dec_max],
                [0, self.dec_max],
                [0, self.dec_min],
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


class HorizonExtentMaskMixin:
    """Experimental"""

    @cache
    def _extent_mask_original(self):
        """
        Returns shapely geometry objects of extent (RA = 0...360)

        If the extent crosses equinox, then a MultiPolygon will be returned
        """
        if self.ra_max <= 360:
            coords = [
                [self.ra_min, self.dec_min],
                [self.ra_max, self.dec_min],
                [self.ra_max, self.dec_max],
                [self.ra_min, self.dec_max],
                [self.ra_min, self.dec_min],
            ]
            return Polygon(coords)

        else:
            coords_1 = [
                [self.ra_min, self.dec_min],
                [360, self.dec_min],
                [360, self.dec_max],
                [self.ra_min, self.dec_max],
                [self.ra_min, self.dec_min],
            ]
            coords_2 = [
                [0, self.dec_min],
                [(self.ra_max - 360), self.dec_min],
                [(self.ra_max - 360), self.dec_max],
                [0, self.dec_max],
                [0, self.dec_min],
            ]

            return MultiPolygon(
                [
                    Polygon(coords_1),
                    Polygon(coords_2),
                ]
            )

    @cache
    def _extent_mask2(self):
        locations = [
            self.location.at(self.observer.timescale).from_altaz(
                alt_degrees=self.alt[0], az_degrees=self._az[0]
            ),  # lower left
            self.location.at(self.observer.timescale).from_altaz(
                alt_degrees=self.alt[0], az_degrees=self._az[1]
            ),  # lower right
            self.location.at(self.observer.timescale).from_altaz(
                alt_degrees=self.alt[1], az_degrees=self._az[1]
            ),  # upper right
            self.location.at(self.observer.timescale).from_altaz(
                alt_degrees=self.alt[1], az_degrees=self.center_az
            ),  # top center
            # self.location.at(self.observer.timescale).from_altaz(
            #     alt_degrees=self.center_alt, az_degrees=self.center_az
            # ),  # center
            self.location.at(self.observer.timescale).from_altaz(
                alt_degrees=self.alt[1], az_degrees=self._az[0]
            ),  # upper left
            self.location.at(self.observer.timescale).from_altaz(
                alt_degrees=self.alt[0], az_degrees=self._az[0]
            ),  # lower left
        ]

        # self.ra_min = None
        # self.ra_max = None
        # self.dec_max = None
        # self.dec_min = None
        from pprint import pprint
        from shapely import segmentize

        self.location.at(self.observer.timescale).from_altaz(
            alt_degrees=self.center_alt, az_degrees=self.center_az
        )  # center
        print(self.alt)
        print(self._az)

        coords = []
        for location in locations:
            ra, dec, _ = location.radec()
            ra = ra.hours * 15
            if ra < 180:
                ra += 360
            dec = dec.degrees
            coords.append([float(ra), float(dec)])

        pprint(coords)
        # coords = reversed(coords)
        extent = Polygon(coords)

        extent = segmentize(extent, max_segment_length=2)

        self.polygon(style__fill_color="red", style__alpha=0.3, geometry=extent)
        # print(extent)

        return extent

    @profile
    @cache
    def _extent_mask2(self):
        """generally working"""
        coords = []

        alt0, alt1 = self._alt
        az0, az1 = self._az

        for alt in range(0, 90, 5):
            for az in range(az0 - 30, az1 + 30, 5):
                ra, dec, _ = (
                    self.location.at(self.observer.timescale)
                    .from_altaz(alt_degrees=alt, az_degrees=az)
                    .radec()
                )
                ra = ra.hours * 15
                if ra < 180:
                    ra += 360
                dec = dec.degrees
                coords.append([float(ra), float(dec)])

        extent = Polygon(coords)
        from shapely import segmentize

        extent = segmentize(extent, max_segment_length=1)

        self.polygon(style__fill_color="red", style__alpha=0.3, geometry=extent)
        # print(extent)

        return extent

    @profile
    @cache
    def _extent_mask1(self):
        from shapely import segmentize

        mask_altaz = self._extent_mask_altaz()

        altaz_polygons = []

        if str(mask_altaz.geom_type) == "MultiPolygon":
            altaz_polygons = [
                segmentize(p, max_segment_length=5) for p in mask_altaz.geoms
            ]
        else:
            altaz_polygons = [segmentize(mask_altaz, max_segment_length=5)]

        radec_polygons = []

        for p in altaz_polygons:
            coords = []

            for az, alt in list(zip(*p.exterior.coords.xy)):
                ra, dec, _ = (
                    self.location.at(self.observer.timescale)
                    .from_altaz(alt_degrees=alt, az_degrees=az)
                    .radec()
                )
                ra = ra.hours * 15
                if ra < 180:
                    ra += 360
                dec = dec.degrees
                coords.append([float(ra), float(dec)])

            radec_polygons.append(Polygon(coords))

        mp = MultiPolygon(radec_polygons)
        extent = mp.convex_hull

        # extent = segmentize(extent, max_segment_length=1)

        print(extent.area)

        # self.polygon(
        #     style__fill_color="red",
        #     style__alpha=0.3,
        #     geometry=extent
        # )
        # print(extent)

        return extent

    def _axes_to_azalt(self, x: float, y: float) -> tuple[float, float]:
        trans = self.ax.transAxes + self.ax.transData.inverted()
        x_projected, y_projected = self.ax.transAxes.inverted().transform((x, y))
        x_projected, y_projected = trans.transform((x, y))  # axes to data
        az, alt = self._crs.transform_point(x_projected, y_projected, self._proj)
        return float(az), float(alt)

    @profile
    @cache
    def _extent_mask(self):
        coords = []
        azalt = []

        az0, az1 = int(self.az[0]), int(self.az[1])
        alt0, alt1 = int(self.alt[0]), int(self.alt[1])

        for az in range(az0, az1, 5):
            for alt in range(alt0, alt1, 5):
                # ax = x / 100
                # ay = y / 100

                # az, alt = self._axes_to_azalt(ax, ay)

                if az > 360:
                    az -= 360

                azalt.append([az, alt])
                ra, dec, _ = (
                    self.location.at(self.observer.timescale)
                    .from_altaz(alt_degrees=alt, az_degrees=az)
                    .radec()
                )
                ra = float(ra.hours * 15)
                dec = float(dec.degrees)

                if dec > 75:
                    dec = 90

                if ra < 180:
                    ra += 360
                coords.append([float(ra), float(dec)])

                # if prev_ra is not None and abs(ra - prev_ra) > 180:
                #     current_polygon_coords += [current_polygon_coords[0]]
                #     polygon_coords.append(
                #         current_polygon_coords
                #     )
                #     current_polygon_coords = [[ra, dec]]
                # else:
                #     current_polygon_coords.append([ra, dec])

                # prev_ra = ra

        # if current_polygon_coords:
        #     current_polygon_coords += [current_polygon_coords[0]]
        #     polygon_coords.append(current_polygon_coords)
        #     print(current_polygon_coords)

        # print(len(polygon_coords))
        from starplot.geometry import split_polygon_at_360

        # polygons = split_polygon_at_zero(extent)

        from shapely import convex_hull, MultiPoint
        from pprint import pprint

        # extent = MultiPolygon([Polygon(c) for c in polygon_coords])
        # extent = Polygon(coords)
        extent = convex_hull(MultiPoint(coords))
        polygons = split_polygon_at_360(extent)

        pprint(polygons)

        # extent = extent.convex_hull
        # from shapely import segmentize
        # polygons = [segmentize(p, max_segment_length=1) for p in polygons]
        mpoly = MultiPolygon(polygons)

        for p in mpoly.geoms:
            self.polygon(style__fill_color="red", style__alpha=0.3, geometry=p)

        # print(extent)

        return mpoly

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
        from starplot import MapPlot, geod

        ex = geod.rectangle(
            center=(self.ra, self.dec),
            height_degrees=height_degrees,
            width_degrees=width_degrees,
        )
        ra_min = ex[0][0]
        ra_max = ex[2][0]
        dec_min = ex[0][1]
        dec_max = ex[2][1]

        # handle wrapping
        if ra_max < ra_min:
            ra_max += 360

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
            *args,
            **kwargs,
        )
