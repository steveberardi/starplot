import datetime
import warnings

from enum import Enum

from cartopy import crs as ccrs
from matplotlib import pyplot as plt
from matplotlib import patches
from matplotlib.ticker import FuncFormatter, FixedLocator
import geopandas as gpd
import numpy as np
import pyproj

from pyongc import ongc
from skyfield.api import Star

from starplot.base import StarPlot
from starplot.data import load, DataFiles, bayer, constellations, stars, ecliptic, dsos
from starplot.models import SkyObject
from starplot.styles import PlotStyle, PolygonStyle, MAP_BASE
from starplot.utils import lon_to_ra, dec_str_to_float

# Silence noisy cartopy warnings
warnings.filterwarnings("ignore", module="cartopy")

DEFAULT_FOV_STYLE = PolygonStyle(
    fill=False, edge_color="red", line_style="dashed", edge_width=4, zorder=1000
)
"""Default style for plotting scope and bino views"""


class Projection(str, Enum):
    """Supported projections for MapPlots"""

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
        ra_min: Minimum right ascension (hours) of the map
        ra_max: Maximum right ascension (hours) of the map
        dec_min: Minimum declination (degrees) of the map
        dec_max: Maximum declination (degrees) of the map
        dt: Date/time to use for star/planet positions, (*must be timezone-aware*). Default = current UTC time.
        limiting_magnitude: Limiting magnitude of stars to plot
        limiting_magnitude_labels: Limiting magnitude of stars to label on the plot
        ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        style: Styling for the plot (colors, sizes, fonts, etc)
        resolution: Size (in pixels) of largest dimension of the map
        hide_colliding_labels: If True, then labels will not be plotted if they collide with another existing label
        adjust_text: If True, then the labels will be adjusted to avoid overlapping
        star_catalog: The catalog of stars to use: "hipparcos" or "tycho-1" -- Hipparcos is the default and has about 10x less stars than Tycho-1 but will also plot much faster
        rasterize_stars: If True, then the stars will be rasterized when plotted, which can speed up exporting to SVG and reduce the file size but with a loss of image quality

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
        style: PlotStyle = MAP_BASE,
        resolution: int = 2048,
        hide_colliding_labels: bool = True,
        adjust_text: bool = False,
        star_catalog: stars.StarCatalog = stars.StarCatalog.HIPPARCOS,
        rasterize_stars: bool = False,
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
        self.star_catalog = star_catalog
        self.rasterize_stars = rasterize_stars

        self._geodetic = ccrs.Geodetic()
        self._plate_carree = ccrs.PlateCarree()
        self._init_plot()

    def _plot_kwargs(self) -> dict:
        # return dict(transform=ccrs.PlateCarree())
        return dict(transform=self._geodetic)

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

        # ensures constellation lines are straight in all supported projections
        if self.projection == Projection.MERCATOR:
            transform = self._plate_carree
        else:
            transform = self._geodetic

        constellation_lines = gpd.read_file(DataFiles.CONSTELLATION_LINES)
        constellation_lines.plot(
            ax=self.ax,
            **self.style.constellation.line.matplot_kwargs(
                size_multiplier=self._size_multiplier
            ),
            transform=transform,
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
            transform=self._plate_carree,
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
        stardata = stars.load(self.star_catalog)
        eph = load(self.ephemeris)
        earth = eph["earth"]

        ra_buffer = (self.ra_max - self.ra_min) / 4
        dec_buffer = (self.dec_max - self.dec_min) / 4

        nearby_stars_df = stardata[
            (stardata["magnitude"] <= self.limiting_magnitude)
            & (stardata["ra_hours"] < self.ra_max + ra_buffer)
            & (stardata["ra_hours"] > self.ra_min - ra_buffer)
            & (stardata["dec_degrees"] < self.dec_max + dec_buffer)
            & (stardata["dec_degrees"] > self.dec_min - dec_buffer)
        ]
        nearby_stars = Star.from_dataframe(nearby_stars_df)
        astrometric = earth.at(self.timescale).observe(nearby_stars)
        stars_ra, stars_dec, _ = astrometric.radec()

        sizes = []
        alphas = []
        for m in nearby_stars_df["magnitude"]:
            if m < 1.6:
                sizes.append((9 - m) ** 2.85 * self._size_multiplier)
                alphas.append(1)
            elif m < 4.6:
                sizes.append((8 - m) ** 2.92 * self._size_multiplier)
                alphas.append(1)
            elif m < 5.8:
                sizes.append((9 - m) ** 2.46 * self._size_multiplier)
                alphas.append(0.9)
            else:
                sizes.append(2.23 * self._size_multiplier)
                alphas.append((16 - m) * 0.09)

        # Plot Stars
        if self.style.star.marker.visible:
            self.ax.scatter(
                *self._prepare_coords(stars_ra.hours, stars_dec.degrees),
                sizes,
                zorder=self.style.star.marker.zorder,
                color=self.style.star.marker.color.as_hex(),
                edgecolors=self.style.star.marker.edge_color.as_hex()
                if self.style.star.marker.edge_color
                else "none",
                rasterized=self.rasterize_stars,
                alpha=alphas,
                **self._plot_kwargs(),
            )
            self._add_legend_handle_marker("Star", self.style.star.marker)

        # Plot star labels (names and bayer designations)
        stars_labeled = nearby_stars_df[
            (nearby_stars_df["magnitude"] <= self.limiting_magnitude_labels)
            & (nearby_stars_df["ra_hours"] <= self.ra_max)
            & (nearby_stars_df["ra_hours"] >= self.ra_min)
            & (nearby_stars_df["dec_degrees"] <= self.dec_max)
            & (nearby_stars_df["dec_degrees"] >= self.dec_min)
        ]

        stars_labeled.sort_values("magnitude")

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

    def _plot_ecliptic(self):
        if not self.style.ecliptic.line.visible:
            return

        x = [-1 * (ra * 15 - 360) for ra, dec in ecliptic.RA_DECS]
        y = [dec for ra, dec in ecliptic.RA_DECS]

        self.ax.plot(
            x,
            y,
            dash_capstyle=self.style.ecliptic.line.dash_capstyle,
            **self.style.ecliptic.line.matplot_kwargs(self._size_multiplier),
            **self._plot_kwargs(),
        )

        if self.style.ecliptic.label.visible:
            inbounds = []
            for ra, dec in ecliptic.RA_DECS:
                if self.in_bounds(ra, dec):
                    inbounds.append((ra, dec))

            if len(inbounds) > 4:
                label_spacing = int(len(inbounds) / 3) or 1

                for i in range(0, len(inbounds), label_spacing):
                    ra, dec = inbounds[i]
                    self._plot_text(
                        ra,
                        dec - 0.4,
                        "ECLIPTIC",
                        **self.style.ecliptic.label.matplot_kwargs(
                            self._size_multiplier
                        ),
                    )

    def _plot_celestial_equator(self):
        if self.style.celestial_equator.line.visible:
            self.ax.plot(
                [0, 360],
                [0, 0],
                **self.style.celestial_equator.line.matplot_kwargs(
                    self._size_multiplier
                ),
                transform=self._plate_carree,
            )

        if self.style.celestial_equator.label.visible:
            style = self.style.celestial_equator.label.matplot_kwargs(
                self._size_multiplier
            )

            label_spacing = (self.ra_max - self.ra_min) / 3
            for ra in np.arange(self.ra_min, self.ra_max, label_spacing):
                self._plot_text(ra, 0.25, "CELESTIAL EQUATOR", **style)

    def _plot_gridlines(self):
        labels_visible = self.style.gridlines.label.visible
        lines_visible = self.style.gridlines.line.visible

        def ra_formatter(x, pos) -> str:
            hour, minutes, seconds = lon_to_ra(x)
            return f"{hour}h"

        def dec_formatter(x, pos) -> str:
            return f"{round(x)}\u00b0"

        if lines_visible:
            gridlines = self.ax.gridlines(
                draw_labels=labels_visible,
                x_inline=False,
                y_inline=False,
                rotate_labels=False,
                xpadding=12,
                ypadding=12,
                **self.style.gridlines.line.matplot_kwargs(),
            )

            # use a fixed locator for right ascension so gridlines are only drawn at whole numbers
            hour_locations = [x for x in range(-180, 180, 15)]
            gridlines.xlocator = FixedLocator(hour_locations)
            gridlines.xformatter = FuncFormatter(ra_formatter)
            gridlines.xlabel_style = self.style.gridlines.label.matplot_kwargs()

            gridlines.yformatter = FuncFormatter(dec_formatter)
            gridlines.ylabel_style = self.style.gridlines.label.matplot_kwargs()

    def _plot_tick_marks(self):
        if not self.style.tick_marks.visible:
            return

        xticks = [x for x in np.arange(-180, 180, 3.75)]
        yticks = [x for x in np.arange(-90, 90, 1)]
        tick_style = self.style.tick_marks.matplot_kwargs()
        tick_style["family"] = "monospace"
        xtick_style = tick_style.copy()
        xtick_style["fontsize"] -= 4
        xtick_style["weight"] = "heavy"

        self.ax.gridlines(
            draw_labels=True,
            xlocs=xticks,
            ylocs=yticks,
            x_inline=False,
            y_inline=False,
            rotate_labels=False,
            xpadding=0.34,
            ypadding=0.34,
            yformatter=FuncFormatter(lambda x, pos: "—"),
            xformatter=FuncFormatter(lambda x, pos: "|"),
            xlabel_style=xtick_style,
            ylabel_style=tick_style,
            alpha=0,  # hide the actual gridlines
        )

    def _plot_dsos(self):
        nearby_dsos = ongc.listObjects(
            minra=self.ra_min * 15,  # convert to degrees (0-360)
            maxra=self.ra_max * 15,  # convert to degrees (0-360)
            mindec=self.dec_min,
            maxdec=self.dec_max,
            uptovmag=self.limiting_magnitude,
        )

        styles = {
            # Star Clusters ----------
            dsos.Type.OPEN_CLUSTER: self.style.dso_open_cluster,
            dsos.Type.GLOBULAR_CLUSTER: self.style.dso_globular_cluster,
            # Galaxies ----------
            dsos.Type.GALAXY: self.style.dso_galaxy,
            dsos.Type.GALAXY_PAIR: self.style.dso_galaxy,
            dsos.Type.GALAXY_TRIPLET: self.style.dso_galaxy,
            dsos.Type.GROUP_OF_GALAXIES: self.style.dso_galaxy,
            # Nebulas ----------
            dsos.Type.NEBULA: self.style.dso_nebula,
            dsos.Type.PLANETARY_NEBULA: self.style.dso_nebula,
            dsos.Type.EMISSION_NEBULA: self.style.dso_nebula,
            dsos.Type.STAR_CLUSTER_NEBULA: self.style.dso_nebula,
            dsos.Type.REFLECTION_NEBULA: self.style.dso_nebula,
            # Stars ----------
            dsos.Type.STAR: None,
            dsos.Type.DOUBLE_STAR: self.style.dso_double_star,
            dsos.Type.ASSOCIATION_OF_STARS: self.style.dso,
            # Undefined - TODO
            "Dark Nebula": None,
            "HII Ionized region": None,
            "Supernova remnant": None,
            "Nova star": None,
            "Nonexistent object": None,
            "Object of other/unknown type": None,
            "Duplicated record": None,
        }
        legend_labels = {
            # Galaxies ----------
            dsos.Type.GALAXY: "Galaxy",
            dsos.Type.GALAXY_PAIR: "Galaxy",
            dsos.Type.GALAXY_TRIPLET: "Galaxy",
            dsos.Type.GROUP_OF_GALAXIES: "Galaxy",
            # Nebulas ----------
            dsos.Type.NEBULA: "Nebula",
            dsos.Type.PLANETARY_NEBULA: "Nebula",
            dsos.Type.EMISSION_NEBULA: "Nebula",
            dsos.Type.STAR_CLUSTER_NEBULA: "Nebula",
            dsos.Type.REFLECTION_NEBULA: "Nebula",
        }

        for d in nearby_dsos:
            if d.coords is None:
                continue

            ra = d.coords[0][0] + d.coords[0][1] / 60 + d.coords[0][2] / 3600
            dec = dec_str_to_float(d.dec)
            style = styles.get(d.type)

            # only plot DSOs with defined styles
            if style:
                obj = SkyObject(
                    name=d.name,
                    ra=ra,
                    dec=dec,
                    style=style,
                )
                legend_label = legend_labels.get(d.type) or d.type
                self._add_legend_handle_marker(legend_label, obj.style.marker)
                self.plot_object(obj)

    def _fit_to_ax(self) -> None:
        bbox = self.ax.get_window_extent().transformed(
            self.fig.dpi_scale_trans.inverted()
        )
        width, height = bbox.width, bbox.height
        self.fig.set_size_inches(width, height)

    def _compute_radius(self, radius_degrees: float, x: float = 0, y: float = 0):
        geod = pyproj.Geod("+a=6378137 +f=0.0", sphere=True)
        _, _, distance = geod.inv(x, y, x + radius_degrees, y)
        return distance

    def _plot_fov_circle(
        self, ra, dec, fov, magnification, style: PolygonStyle = DEFAULT_FOV_STYLE
    ):
        # FOV (degrees) = FOV eyepiece / magnification
        fov_degrees = fov / magnification
        lon, lat = self._prepare_coords(ra, dec)
        fov_radius = fov_degrees / 2
        radius = self._compute_radius(fov_radius)
        x, y = self._proj.transform_point(lon, lat, ccrs.Geodetic())

        p = patches.Circle(
            (x, y),
            radius=radius,
            **style.matplot_kwargs(self._size_multiplier),
        )
        self.ax.add_patch(p)

    def plot_scope_fov(
        self,
        ra: float,
        dec: float,
        scope_focal_length: float,
        eyepiece_focal_length: float,
        eyepiece_fov: float,
        style: PolygonStyle = DEFAULT_FOV_STYLE,
    ):
        """Draws a circle representing the field of view for a telescope and eyepiece.

        Args:
            ra: Right ascension of the center of view
            dec: Declination of the center of view
            scope_focal_length: focal length (mm) of the scope
            eyepiece_focal_length: focal length (mm) of the eyepiece
            eyepiece_fov: field of view (degrees) of the eyepiece
            style: style of the polygon
        """
        # FOV (degrees) = FOV eyepiece / magnification
        magnification = scope_focal_length / eyepiece_focal_length
        self._plot_fov_circle(ra, dec, eyepiece_fov, magnification, style)

    def plot_bino_fov(
        self,
        ra: float,
        dec: float,
        fov: float,
        magnification: float,
        style: PolygonStyle = DEFAULT_FOV_STYLE,
    ):
        """Draws a circle representing the field of view for binoculars.

        Args:
            ra: Right ascension of the center of view
            dec: Declination of the center of view
            fov: field of view (degrees) of the binoculars
            magnification: magnification of the binoculars
            style: style of the polygon
        """
        self._plot_fov_circle(ra, dec, fov, magnification, style)

    def _init_plot(self):
        self.fig = plt.figure(
            figsize=(self.figure_size, self.figure_size),
            facecolor=self.style.border_bg_color.as_hex(),
            layout="constrained",
        )

        if self.projection in [Projection.STEREO_NORTH, Projection.STEREO_SOUTH]:
            # for stereo projections, try to orient map so the pole is "up"
            bounds = self._latlon_bounds()
            center_lon = (bounds[0] + bounds[1]) / 2
        else:
            center_lon = -180

        self._proj = Projection.crs(self.projection, center_lon)
        self._proj.threshold = 100
        self.ax = plt.axes(projection=self._proj)
        self.ax.set_extent(self._latlon_bounds(), crs=self._plate_carree)
        self.ax.set_facecolor(self.style.background_color.as_hex())
        self._adjust_radec_minmax()

        self._plot_gridlines()
        self._plot_tick_marks()
        self._plot_constellation_lines()
        self._plot_constellation_borders()
        self._plot_constellation_labels()
        self._plot_milky_way()
        self._plot_stars()
        self._plot_ecliptic()
        self._plot_celestial_equator()
        self._plot_dsos()
        self._plot_planets()
        self._plot_moon()

        self._fit_to_ax()

        self.refresh_legend()

        if self.adjust_text:
            self.adjust_labels()
