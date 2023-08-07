import datetime
import warnings

from enum import Enum

import cartopy.crs as ccrs

from matplotlib import pyplot as plt
import geopandas as gpd

from skyfield.api import Star

from starplot.base import StarPlot
from starplot.data import load, DataFiles, bayer, constellations, stars
from starplot.styles import PlotStyle, MAP_BLUE

# Silence noisy cartopy warnings
warnings.filterwarnings("ignore", module="cartopy")


class Projection(str, Enum):
    """
    Supported projections for MapPlots

    """

    STEREO_NORTH = "stereo_north"
    """Good for objects near the north celestial pole, but distorts objects near the mid declinations"""

    STEREO_SOUTH = "stereo_south"
    """Good for objects near the south celestial pole, but distorts objects near the mid declinations"""

    MERCATOR = "mercator"
    """Good for declinations between -70 and 70, but distorts objects near the poles"""

    @staticmethod
    def crs(projection, center_lon=-180):
        return {
            Projection.STEREO_NORTH: ccrs.NorthPolarStereo(center_lon),
            Projection.STEREO_SOUTH: ccrs.SouthPolarStereo(center_lon),
            Projection.MERCATOR: ccrs.Mercator(center_lon),
        }.get(projection)


class MapPlot(StarPlot):
    """Creates a new map plot.

    Args:
        projection: Projection of the map
        ra_min: Minimum right ascension of the map
        ra_max: Maximum right ascension of the map
        dec_min: Minimum declination of the map
        dec_max: Maximum declination of the map
        dt: Date/time to use for star positions, (*must be timezone-aware*). Default = current UTC time.
        limiting_magnitude: Limiting magnitude of stars to plot
        limiting_magnitude_labels: Limiting magnitude of stars to label on the plot
        ephemeris: Ephemeris to use for calculating star positions
        style: Styling for the plot (colors, sizes, fonts, etc)
        resolution: Size (in pixels) of largest dimension of the map
        hide_colliding_labels: If True, then labels will not be plotted if they collide with another existing label
        adjust_text: If True, then the labels will be adjusted to avoid overlapping

    Returns:
        MapPlot: A new instance of a MapPlot

    """

    def __init__(
        self,
        projection: Projection,
        ra_min: float,
        ra_max: float,
        dec_min: float,
        dec_max: float,
        dt: datetime = None,
        limiting_magnitude: float = 6.0,
        limiting_magnitude_labels: float = 6.0,
        ephemeris: str = "de421_2001.bsp",
        style: PlotStyle = MAP_BLUE,
        resolution: int = 2048,
        hide_colliding_labels: bool = True,
        adjust_text: bool = False,
        *args,
        **kwargs,
    ) -> "MapPlot":
        super().__init__(
            dt,
            limiting_magnitude,
            limiting_magnitude_labels,
            ephemeris,
            style,
            resolution,
            hide_colliding_labels,
            adjust_text,
            *args,
            **kwargs,
        )
        self.projection = projection
        self.ra_min = ra_min
        self.ra_max = ra_max
        self.dec_min = dec_min
        self.dec_max = dec_max
        self._init_plot()

    def _plot_kwargs(self) -> dict:
        return dict(transform=ccrs.PlateCarree())

    def _prepare_coords(self, ra: float, dec: float) -> (float, float):
        return -1 * (ra * 15 - 360), dec

    def in_bounds(self, ra: float, dec: float) -> bool:
        """Determine if a coordinate is within the bounds of the plot.

        Args:
            ra: Right ascension
            dec: Declination

        Returns:
            True if the coordinate is in bounds, otherwise False

        """
        return self.ra_min < ra < self.ra_max and self.dec_min < dec < self.dec_max

    def _latlon_bounds(self):
        # convert the RA/DEC bounds to lat/lon bounds
        return [
            -1 * (self.ra_max * 15 - 360),
            -1 * (self.ra_min * 15 - 360),
            self.dec_min,
            self.dec_max,
        ]

    def _adjust_radec_minmax(self):
        # adjust the RA min/max if the DEC bounds is near the poles
        if self.projection in [Projection.STEREO_NORTH, Projection.STEREO_SOUTH] and (
            self.dec_max > 80 or self.dec_min < -80
        ):
            self.ra_min = 0
            self.ra_max = 24

    def _plot_constellation_lines(self):
        if not self.style.constellation.line.visible:
            return
        constellation_lines = gpd.read_file(DataFiles.CONSTELLATION_LINES)
        constellation_lines.plot(
            ax=self.ax,
            **self.style.constellation.line.matplot_kwargs(
                size_multiplier=self._size_multiplier
            ),
            **self._plot_kwargs(),
        )

    def _plot_constellation_borders(self):
        if not self.style.constellation_borders.visible:
            return
        constellation_borders = gpd.read_file(DataFiles.CONSTELLATION_BORDERS)
        constellation_borders.plot(
            ax=self.ax,
            **self.style.constellation_borders.matplot_kwargs(
                size_multiplier=self._size_multiplier
            ),
            **self._plot_kwargs(),
        )

    def _plot_constellation_labels(self):
        if not self.style.constellation.label.visible:
            return
        style = self.style.constellation.label.matplot_kwargs(
            size_multiplier=self._size_multiplier
        )
        for con in constellations.iterator():
            fullname, ra, dec = constellations.get(con)
            if self.in_bounds(ra, dec):
                self._plot_text(ra, dec, con.upper(), **style)

    def _plot_milky_way(self):
        if not self.style.milky_way.visible:
            return
        mw = gpd.read_file(DataFiles.MILKY_WAY)
        mw.plot(
            ax=self.ax,
            **self.style.milky_way.matplot_kwargs(
                size_multiplier=self._size_multiplier
            ),
            **self._plot_kwargs(),
        )

    def _plot_stars(self):
        stardata = stars.load()
        eph = load(self.ephemeris)
        earth = eph["earth"]
        nearby_stars_df = stardata[
            (stardata["magnitude"] <= self.limiting_magnitude)
            & (stardata["ra_hours"] < self.ra_max + 5)
            & (stardata["ra_hours"] > self.ra_min - 5)
            & (stardata["dec_degrees"] < self.dec_max + 10)
            & (stardata["dec_degrees"] > self.dec_min - 10)
        ]
        nearby_stars = Star.from_dataframe(nearby_stars_df)
        astrometric = earth.at(self.timescale).observe(nearby_stars)
        stars_ra, stars_dec, _ = astrometric.radec()

        sizes = []
        for m in nearby_stars_df["magnitude"]:
            if m < 4.6:
                sizes.append((8 - m) ** 2.36 * self._size_multiplier)
            else:
                sizes.append(0.75 * self._size_multiplier)

        # Plot Stars
        if self.style.star.marker.visible:
            self.ax.scatter(
                *self._prepare_coords(stars_ra.hours, stars_dec.degrees),
                sizes,
                zorder=100,
                color=self.style.star.marker.color.as_hex(),
                **self._plot_kwargs(),
            )

        # Plot star labels (names and bayer designations)
        stars_labeled = nearby_stars_df[
            (nearby_stars_df["magnitude"] <= self.limiting_magnitude_labels)
            & (nearby_stars_df["ra_hours"] <= self.ra_max)
            & (nearby_stars_df["ra_hours"] >= self.ra_min)
            & (nearby_stars_df["dec_degrees"] <= self.dec_max)
            & (nearby_stars_df["dec_degrees"] >= self.dec_min)
        ]

        for hip_id, s in stars_labeled.iterrows():
            name = stars.hip_names.get(hip_id)
            bayer_desig = bayer.hip.get(hip_id)
            ra, dec = s["ra_hours"], s["dec_degrees"]

            if name and self.style.star.label.visible:
                style = self.style.star.label.matplot_kwargs(self._size_multiplier)
                self._plot_text(
                    ra - 0.01, dec - 0.12, name, ha="left", va="top", **style
                )

            if bayer_desig and self.style.bayer_labels.visible:
                style = self.style.bayer_labels.matplot_kwargs(self._size_multiplier)
                self._plot_text(
                    ra + 0.01, dec, bayer_desig, ha="right", va="bottom", **style
                )

    def _init_plot(self):
        self.fig = plt.figure(figsize=(self.figure_size, self.figure_size))

        if self.projection in [Projection.STEREO_NORTH, Projection.STEREO_SOUTH]:
            # for stereo projections, try to orient map so the pole is "up"
            bounds = self._latlon_bounds()
            center_lon = (bounds[0] + bounds[1]) / 2
        else:
            center_lon = -180

        self.ax = plt.axes(projection=Projection.crs(self.projection, center_lon))
        self.ax.set_extent(self._latlon_bounds(), crs=ccrs.PlateCarree())
        self._adjust_radec_minmax()

        gridlines = self.ax.gridlines(zorder=-1000, draw_labels=False)
        gridlines.top_labels = False
        gridlines.right_labels = False

        self._plot_constellation_lines()
        self._plot_constellation_borders()
        self._plot_constellation_labels()
        self._plot_milky_way()
        self._plot_stars()

        if self.adjust_text:
            self.adjust_labels()
