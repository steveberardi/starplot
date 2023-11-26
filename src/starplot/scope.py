from datetime import datetime

from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

from skyfield.api import Star, wgs84
from skyfield.positionlib import position_of_radec
from skyfield.projections import build_stereographic_projection

from starplot.base import StarPlot
from starplot.data import load, constellations, stars, dsos, ecliptic
from starplot.styles import PlotStyle, ZENITH_BASE
from starplot.utils import in_circle



class ScopePlot(StarPlot):
    """Creates a new scope plot.

    Args:
        lat: Latitude of viewing location
        lon: Longitude of viewing location
        include_info_text: If True, then the plot will include the time/location
        dt: Date/time to use for star/planet positions (*must be timezone-aware*). Default = current UTC time.
        limiting_magnitude: Limiting magnitude of stars to plot
        limiting_magnitude_labels: Limiting magnitude of stars to label on the plot
        ephemeris: Ephemeris to use for calculating star positions
        style: Styling for the plot (colors, sizes, fonts, etc)
        resolution: Size (in pixels) of largest dimension of the map
        hide_colliding_labels: If True, then labels will not be plotted if they collide with another existing label
        adjust_text: If True, then the labels will be adjusted to avoid overlapping

    Returns:
        ZenithPlot: A new instance of a ZenithPlot

    """

    def __init__(
        self,
        lat: float = None,
        lon: float = None,
        include_info_text: bool = False,
        dt: datetime = None,
        limiting_magnitude: float = 6.0,
        limiting_magnitude_labels: float = 2.1,
        ephemeris: str = "de421_2001.bsp",
        style: PlotStyle = ZENITH_BASE,
        resolution: int = 2048,
        hide_colliding_labels: bool = True,
        adjust_text: bool = False,
        *args,
        **kwargs,
    ) -> "ScopePlot":
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
        self.lat = lat
        self.lon = lon
        self.include_info_text = include_info_text

        self._calc_position()
        self._init_plot()

    def in_bounds(self, ra, dec) -> bool:
        x, y = self._prepare_coords(ra, dec)
        result = in_circle(x, y)
        return result

    def _prepare_coords(self, ra, dec) -> (float, float):
        return self.project_fn(position_of_radec(ra, dec))

    def _calc_position(self):
        self.position = wgs84.latlon(self.lat, self.lon).at(self.timescale)
        

    def _plot_stars(self):
        stardata = stars.load(limiting_magnitude=self.limiting_magnitude)
        self._stardata = stardata

        eph = load(self.ephemeris)
        earth = eph["earth"]

        m45 = Star(ra_hours=(3, 47, 29), dec_degrees=(24, 6, 0))

        nearby_stars_df = stardata[
            (stardata["magnitude"] <= self.limiting_magnitude)
            & (stardata["ra_hours"] < 5)
            & (stardata["ra_hours"] > 3)
            & (stardata["dec_degrees"] < 26)
            & (stardata["dec_degrees"] > 24)
        ]
        
        location = earth + wgs84.latlon(self.lat, self.lon)
        star_positions = location.at(self.timescale).observe(m45)
        
        app = star_positions.apparent()
        
        alt, az, distance = app.altaz()

        x = []
        y = []
        sizes = []

        for _, star in nearby_stars_df.iterrows():
            m = star["magnitude"]

            if m < 2:
                sizes.append((8 - m) ** 2.56 * (self._size_multiplier**2))
            elif m < 8:
                sizes.append((8 - m) ** 1.38 * (self._size_multiplier**2))
            else:
                sizes.append(self._size_multiplier**2)

            s = Star(ra_hours=star["ra_hours"], dec_degrees=star["dec_degrees"])
            pos = location.at(self.timescale).observe(s)
            app = pos.apparent()
            alt, az, _ = app.altaz()
            x.append(az.degrees)
            y.append(alt.degrees)
       
        # Draw stars
        if self.style.star.marker.visible:
            self._plotted_stars = self.ax.scatter(
                x,
                y,
                sizes,
                color=self.style.star.marker.color.as_hex(),
            )

       

    def _plot_border(self):
        # Plot border text
        border_font_kwargs = dict(
            fontsize=self.style.border_font_size * self._size_multiplier * 2,
            weight=self.style.border_font_weight,
            color=self.style.border_font_color.as_hex(),
        )
        self.ax.text(0, 1.009, "N", **border_font_kwargs)
        self.ax.text(1.003, 0, "W", **border_font_kwargs)
        self.ax.text(-1.042, 0, "E", **border_font_kwargs)
        self.ax.text(0, -1.045, "S", **border_font_kwargs)

        # Background Circle
        self.background_circle = plt.Circle(
            (0, 0),
            facecolor=self.style.background_color.as_hex(),
            radius=1.0,
            linewidth=0,
            fill=True,
            zorder=-100,
        )
        self.ax.add_patch(self.background_circle)

        # Border Circles
        inner_border = plt.Circle(
            (0, 0),
            radius=1.0,
            linewidth=2 * self._size_multiplier,
            edgecolor=self.style.border_line_color.as_hex(),
            fill=False,
            zorder=100,
        )
        self.ax.add_patch(inner_border)

        # Outer border circle
        outer_border = plt.Circle(
            (0, 0),
            facecolor=self.style.border_bg_color.as_hex(),
            radius=1.06,
            linewidth=4 * self._size_multiplier,
            edgecolor=self.style.border_line_color.as_hex(),
            fill=True,
            zorder=-1024,
        )
        self.ax.add_patch(outer_border)

    def _init_plot(self):
        self.fig = plt.figure(figsize=(self.figure_size, self.figure_size))
        self.ax = plt.axes()

        # self.ax.set_xlim(-1.1, 1.1)
        # self.ax.set_ylim(-1.1, 1.1)
        # self.ax.xaxis.set_visible(False)
        # self.ax.yaxis.set_visible(False)
        # self.ax.set_aspect(1.0)
        # self.ax.axis("off")

        # self._plot_border()
        self._plot_stars()

        # if self.include_info_text:
        #     font_size = self.style.legend.font_size * self._size_multiplier * 2
        #     dt_str = self.dt.strftime("%m/%d/%Y @ %H:%M:%S") + " " + self.dt.tzname()
        #     info = f"{str(self.lat)}, {str(self.lon)}\n{dt_str}"
        #     self.ax.text(
        #         -1.03,
        #         -1.03,
        #         info,
        #         fontsize=font_size,
        #         family="monospace",
        #         linespacing=2,
        #     )

