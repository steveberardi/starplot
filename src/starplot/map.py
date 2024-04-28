import datetime
import math
import warnings
from typing import Callable

from cartopy import crs as ccrs
from matplotlib import pyplot as plt
from matplotlib import path, patches, ticker
from matplotlib.ticker import FuncFormatter, FixedLocator
from shapely import LineString, MultiLineString
from shapely.ops import unary_union
from skyfield.api import Star as SkyfieldStar, wgs84
import geopandas as gpd
import numpy as np

from starplot.base import BasePlot
from starplot.data import DataFiles, constellations as condata, stars
from starplot.data.constellations import CONSTELLATIONS_FULL_NAMES
from starplot.mixins import ExtentMaskMixin
from starplot.plotters import StarPlotterMixin, DsoPlotterMixin
from starplot.projections import Projection
from starplot.styles import (
    LabelStyle,
    LineStyle,
    PlotStyle,
    PolygonStyle,
    PathStyle,
    extensions,
)
from starplot.styles.helpers import use_style
from starplot.utils import lon_to_ra, ra_to_lon

# Silence noisy cartopy warnings
warnings.filterwarnings("ignore", module="cartopy")
warnings.filterwarnings("ignore", module="shapely")

DEFAULT_MAP_STYLE = PlotStyle().extend(extensions.MAP)


class MapPlot(BasePlot, ExtentMaskMixin, StarPlotterMixin, DsoPlotterMixin):
    """Creates a new map plot.

    !!! star "Note"
        **`lat`, `lon`, and `dt` are required for perspective projections (`Orthographic`, `Stereographic`, and `Zenith`)**

    Args:
        projection: Projection of the map
        ra_min: Minimum right ascension of the map's extent, in hours (0...24)
        ra_max: Maximum right ascension of the map's extent, in hours (0...24)
        dec_min: Minimum declination of the map's extent, in degrees (-90...90)
        dec_max: Maximum declination of the map's extent, in degrees (-90...90)
        lat: Latitude for perspective projections: Orthographic, Stereographic, and Zenith
        lon: Longitude for perspective projections: Orthographic, Stereographic, and Zenith
        dt: Date/time to use for star/planet positions, (*must be timezone-aware*). Default = current UTC time.
        ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        style: Styling for the plot (colors, sizes, fonts, etc)
        resolution: Size (in pixels) of largest dimension of the map
        hide_colliding_labels: If True, then labels will not be plotted if they collide with another existing label

    Returns:
        MapPlot: A new instance of a MapPlot

    """

    def __init__(
        self,
        projection: Projection,
        ra_min: float = 0,
        ra_max: float = 24,
        dec_min: float = -90,
        dec_max: float = 90,
        lat: float = None,
        lon: float = None,
        dt: datetime = None,
        ephemeris: str = "de421_2001.bsp",
        style: PlotStyle = DEFAULT_MAP_STYLE,
        resolution: int = 2048,
        hide_colliding_labels: bool = True,
        *args,
        **kwargs,
    ) -> "MapPlot":
        super().__init__(
            dt,
            ephemeris,
            style,
            resolution,
            hide_colliding_labels,
            *args,
            **kwargs,
        )
        self.logger.debug("Creating MapPlot...")

        if ra_min > ra_max:
            raise ValueError("ra_min must be less than ra_max")
        if dec_min > dec_max:
            raise ValueError("dec_min must be less than dec_max")
        if dec_min < -90 or dec_max > 90:
            raise ValueError("Declination out of range (must be -90...90)")

        self.projection = projection
        self.ra_min = ra_min
        self.ra_max = ra_max
        self.dec_min = dec_min
        self.dec_max = dec_max
        self.lat = lat
        self.lon = lon

        if self.projection in [
            Projection.ORTHOGRAPHIC,
            Projection.STEREOGRAPHIC,
            Projection.ZENITH,
        ] and (lat is None or lon is None):
            raise ValueError(
                f"lat and lon are required for the {self.projection.value.upper()} projection"
            )

        if self.projection == Projection.ZENITH and not self._is_global_extent():
            raise ValueError(
                "Zenith projection requires a global extent: ra_min=0, ra_max=24, dec_min=-90, dec_max=90"
            )

        self.stars_df = stars.load("hipparcos")

        self._geodetic = ccrs.Geodetic()
        self._plate_carree = ccrs.PlateCarree()
        self._crs = ccrs.CRS(
            proj4_params=[
                ("proj", "latlong"),
                ("axis", "wnu"),  # invert
                ("a", "6378137"),
            ],
            globe=ccrs.Globe(ellipse="sphere", flattening=0),
        )
        self._init_plot()

    def _plot_kwargs(self) -> dict:
        return dict(transform=self._crs)

    def _prepare_coords(self, ra: float, dec: float) -> (float, float):
        return ra * 15, dec

    def in_bounds(self, ra: float, dec: float) -> bool:
        """Determine if a coordinate is within the bounds of the plot.

        Args:
            ra: Right ascension, in hours (0...24)
            dec: Declination, in degrees (-90...90)

        Returns:
            True if the coordinate is in bounds, otherwise False
        """
        # TODO : try using pyproj transformer directly
        x, y = self._proj.transform_point(ra * 15, dec, self._crs)
        data_to_axes = self.ax.transData + self.ax.transAxes.inverted()
        x_axes, y_axes = data_to_axes.transform((x, y))
        return 0 <= x_axes <= 1 and 0 <= y_axes <= 1

    def _in_bounds_xy(self, x: float, y: float) -> bool:
        return self.in_bounds(x / 15, y)

    def _polygon(self, points, style, **kwargs):
        super()._polygon(points, style, transform=self._crs, **kwargs)

    def _latlon_bounds(self):
        # convert the RA/DEC bounds to lat/lon bounds
        return [
            -1 * self.ra_min * 15,
            -1 * self.ra_max * 15,
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

        # adjust declination to match extent
        extent = self.ax.get_extent(crs=self._plate_carree)
        self.dec_min = extent[2]
        self.dec_max = extent[3]

        # adjust right ascension to match extent
        if self.ra_max < 24:
            ra_min = (-1 * extent[1]) / 15
            ra_max = (-1 * extent[0]) / 15

            if ra_min < 0 or ra_max < 0:
                ra_min += 24
                ra_max += 24

            self.ra_min = ra_min
            self.ra_max = ra_max

        self.logger.debug(
            f"Extent = RA ({self.ra_min:.2f}, {self.ra_max:.2f}) DEC ({self.dec_min:.2f}, {self.dec_max:.2f})"
        )

    def _read_geo_package(self, filename: str):
        """Returns GeoDataFrame of a GeoPackage file"""
        extent = self.ax.get_extent(crs=self._plate_carree)
        bbox = (extent[0], extent[2], extent[1], extent[3])

        return gpd.read_file(
            filename,
            engine="pyogrio",
            use_arrow=True,
            bbox=bbox,
        )

    def _load_stars(self, catalog, limiting_magnitude):
        df = super()._load_stars(catalog, limiting_magnitude)

        if self.projection == Projection.ZENITH:
            # filter stars for zenith plots to only include those above horizon
            earth = self.ephemeris["earth"]
            self.location = earth + wgs84.latlon(self.lat, self.lon)

            stars_apparent = (
                self.location.at(self.timescale)
                .observe(SkyfieldStar.from_dataframe(df))
                .apparent()
            )
            # we only need altitude
            stars_alt, _, _ = stars_apparent.altaz()
            df["alt"] = stars_alt.degrees
            df = df[df["alt"] > 0]

        return df

    @use_style(LineStyle, "constellation_borders")
    def constellation_borders(self, style: LineStyle = None):
        """Plots the constellation borders

        Args:
            style: Styling of the constellation borders. If None, then the plot's style (specified when creating the plot) will be used
        """
        constellation_borders = self._read_geo_package(
            DataFiles.CONSTELLATION_BORDERS.value
        )

        if constellation_borders.empty:
            return

        style_kwargs = style.matplot_kwargs(self._size_multiplier)

        geometries = []

        for _, c in constellation_borders.iterrows():
            for ls in c.geometry.geoms:
                geometries.append(ls)

        for ls in geometries:
            x, y = ls.xy
            self.ax.plot(
                list(x),
                list(y),
                transform=self._plate_carree,
                **style_kwargs,
            )

    def _plot_constellation_borders(self):
        """work in progress"""
        constellation_borders = gpd.read_file(
            DataFiles.CONSTELLATIONS.value,
            engine="pyogrio",
            use_arrow=True,
            bbox=self._extent_mask(),
        )

        if constellation_borders.empty:
            return

        geometries = []

        for i, constellation in constellation_borders.iterrows():
            geometry_types = constellation.geometry.geom_type

            # equinox = LineString([[0, 90], [0, -90]])
            """
            Problems:
                - Need to handle multipolygon borders too (SER)
                - Shapely's union doesn't handle geodesy (e.g. TRI + AND)
                - ^^ TRI is plotted with ra < 360, but AND has ra > 360
                - ^^ idea: create union first and then remove duplicate lines?
            
                TODO: create new static data file of constellation border lines
            """

            if "Polygon" in geometry_types and "MultiPolygon" not in geometry_types:
                polygons = [constellation.geometry]

            elif "MultiPolygon" in geometry_types:
                polygons = constellation.geometry.geoms

            for p in polygons:
                coords = list(zip(*p.exterior.coords.xy))
                # coords = [(ra * -1, dec) for ra, dec in coords]

                new_coords = []

                for i, c in enumerate(coords):
                    ra, dec = c
                    if i > 0:
                        if new_coords[i - 1][0] - ra > 60:
                            ra += 360

                        elif ra - new_coords[i - 1][0] > 60:
                            new_coords[i - 1][0] += 360

                    new_coords.append([ra, dec])

                ls = LineString(new_coords)
                geometries.append(ls)

        mls = MultiLineString(geometries)
        geometries = unary_union(mls)

        style_kwargs = self.style.constellation_borders.matplot_kwargs(
            size_multiplier=self._size_multiplier
        )

        for ls in list(geometries.geoms):
            # print(ls)
            x, y = ls.xy
            newx = [xx * -1 for xx in list(x)]
            self.ax.plot(
                # list(x),
                newx,
                list(y),
                # **self._plot_kwargs(),
                # transform=self._geodetic,
                transform=self._plate_carree,
                **style_kwargs,
            )

    @use_style(PathStyle, "constellation")
    def constellations(
        self,
        style: PathStyle = None,
        labels: dict[str, str] = CONSTELLATIONS_FULL_NAMES,
    ):
        """Plots the constellation lines and/or labels

        Args:
            style: Styling of the constellations. If None, then the plot's style (specified when creating the plot) will be used
            labels: A dictionary where the keys are each constellation's 3-letter abbreviation, and the values are how the constellation will be labeled on the plot.
        """
        labels = labels or {}
        constellations_gdf = gpd.read_file(
            DataFiles.CONSTELLATIONS.value,
            engine="pyogrio",
            use_arrow=True,
            bbox=self._extent_mask(),
        )

        if constellations_gdf.empty:
            return

        if self.projection in [Projection.MERCATOR, Projection.MILLER]:
            transform = self._plate_carree
        else:
            transform = self._geodetic

        conline_hips = condata.lines()
        style_kwargs = style.line.matplot_kwargs(size_multiplier=self._size_multiplier)

        for i, c in constellations_gdf.iterrows():
            hiplines = conline_hips[c.id]

            for s1_hip, s2_hip in hiplines:
                s1 = self.stars_df.loc[s1_hip]
                s2 = self.stars_df.loc[s2_hip]

                s1_ra = s1.ra_hours * 15
                s2_ra = s2.ra_hours * 15

                s1_dec = s1.dec_degrees
                s2_dec = s2.dec_degrees

                if s1_ra - s2_ra > 60:
                    s2_ra += 360

                elif s2_ra - s1_ra > 60:
                    s1_ra += 360

                s1_ra *= -1
                s2_ra *= -1

                # make lines straight
                # s1_ra, s1_dec = self._proj.transform_point(s1_ra, s1.dec_degrees, self._geodetic)
                # s2_ra, s2_dec = self._proj.transform_point(s2_ra, s2.dec_degrees, self._geodetic)

                self.ax.plot(
                    [s1_ra, s2_ra],
                    [s1_dec, s2_dec],
                    transform=transform,
                    **style_kwargs,
                )

        self._plot_constellation_labels(style.label, labels)

    def _plot_constellation_labels(
        self,
        style: PathStyle = None,
        labels: dict[str, str] = CONSTELLATIONS_FULL_NAMES,
    ):
        style = style or self.style.constellation.label

        for con in condata.iterator():
            _, ra, dec = condata.get(con)
            text = labels.get(con.lower())
            self.text(text, ra, dec, style)

    @use_style(PolygonStyle, "milky_way")
    def milky_way(self, style: PolygonStyle = None):
        """Plots the Milky Way

        Args:
            style: Styling of the Milky Way. If None, then the plot's style (specified when creating the plot) will be used
        """
        mw = self._read_geo_package(DataFiles.MILKY_WAY.value)

        if not mw.empty:
            style_kwargs = style.matplot_kwargs(size_multiplier=self._size_multiplier)
            style_kwargs.pop("fill", None)

            # create union of all Milky Way patches
            gs = mw.geometry.to_crs(self._plate_carree)
            mw_union = gs.buffer(0.1).unary_union.buffer(-0.1)

            self.ax.add_geometries(
                [mw_union],
                crs=self._plate_carree,
                **style_kwargs,
            )

    @use_style(PolygonStyle)
    def horizon(
        self,
        style: PolygonStyle = PolygonStyle(
            fill_color=None,
            edge_color="red",
            line_style="dashed",
            edge_width=4,
            zorder=1000,
        ),
    ):
        """
        Draws a [great circle](https://en.wikipedia.org/wiki/Great_circle) representing the horizon for the given `lat`, `lon` at time `dt` (so you must define these when creating the plot to use this function)

        Args:
            style: Style of the polygon
        """
        if self.lat is None or self.lon is None or self.dt is None:
            raise ValueError("lat, lon, and dt are required for plotting the horizon")

        self.circle(
            ((self.timescale.gmst + self.lon / 15.0) % 24, self.lat),
            90,
            style,
        )

    @use_style(PathStyle, "gridlines")
    def gridlines(
        self,
        style: PathStyle = None,
        labels: bool = True,
        ra_locations: list[float] = None,
        dec_locations: list[float] = None,
        ra_formatter_fn: Callable[[float], str] = None,
        dec_formatter_fn: Callable[[float], str] = None,
        tick_marks: bool = False,
        ra_tick_locations: list[float] = None,
        dec_tick_locations: list[float] = None,
    ):
        """Plots gridlines

        Args:
            style: Styling of the gridlines. If None, then the plot's style (specified when creating the plot) will be used
            labels: If True, then labels for each gridline will be plotted on the outside of the axes.
            ra_locations: List of Right Ascension locations for the gridlines (in hours, 0...24). Defaults to every 1 hour.
            dec_locations: List of Declination locations for the gridlines (in degrees, -90...90). Defaults to every 10 degrees.
            ra_formatter_fn: Callable for creating labels of right ascension gridlines
            dec_formatter_fn: Callable for creating labels of declination gridlines
            tick_marks: If True, then tick marks will be plotted outside the axis. **Only supported for rectangular projections (e.g. Mercator, Miller)**
            ra_tick_locations: List of Right Ascension locations for the tick marks (in hours, 0...24)
            dec_tick_locations: List of Declination locations for the tick marks (in degrees, -90...90)
        """

        ra_formatter_fn_default = lambda r: f"{math.floor(r)}h"  # noqa: E731
        dec_formatter_fn_default = lambda d: f"{round(d)}\u00b0"  # noqa: E731

        ra_formatter_fn = ra_formatter_fn or ra_formatter_fn_default
        dec_formatter_fn = dec_formatter_fn or dec_formatter_fn_default

        def ra_formatter(x, pos) -> str:
            ra = lon_to_ra(x)
            return ra_formatter_fn(ra)

        def dec_formatter(x, pos) -> str:
            return dec_formatter_fn(x)

        ra_locations = ra_locations or [x for x in range(24)]
        dec_locations = dec_locations or [d for d in range(-90, 90, 10)]

        gridlines = self.ax.gridlines(
            draw_labels=labels,
            x_inline=False,
            y_inline=False,
            rotate_labels=False,
            xpadding=12,
            ypadding=12,
            **style.line.matplot_kwargs(),
        )

        style_kwargs = style.label.matplot_kwargs()
        style_kwargs.pop("va")
        style_kwargs.pop("ha")

        gridlines.xlocator = FixedLocator([ra_to_lon(r) for r in ra_locations])
        gridlines.xformatter = FuncFormatter(ra_formatter)
        gridlines.xlabel_style = style_kwargs

        gridlines.ylocator = FixedLocator(dec_locations)
        gridlines.yformatter = FuncFormatter(dec_formatter)
        gridlines.ylabel_style = style_kwargs

        if tick_marks:
            self._tick_marks(style, ra_tick_locations, dec_tick_locations)

    def _tick_marks(self, style, ra_tick_locations=None, dec_tick_locations=None):
        def in_axes(ra):
            return self.in_bounds(ra, (self.dec_max + self.dec_min) / 2)

        xticks = ra_tick_locations or [x for x in np.arange(0, 24, 0.125)]
        yticks = dec_tick_locations or [x for x in np.arange(-90, 90, 1)]

        inbound_xticks = [ra_to_lon(ra) for ra in xticks if in_axes(ra)]
        self.ax.set_xticks(inbound_xticks, crs=self._plate_carree)
        self.ax.xaxis.set_major_formatter(ticker.NullFormatter())

        inbound_yticks = [y for y in yticks if y < self.dec_max and y > self.dec_min]
        self.ax.set_yticks(inbound_yticks, crs=self._plate_carree)
        self.ax.yaxis.set_major_formatter(ticker.NullFormatter())

        self.ax.tick_params(
            which="major",
            width=1,
            length=8,
            color=style.label.font_color.as_hex(),
            top=True,
            right=True,
        )

    def _fit_to_ax(self) -> None:
        bbox = self.ax.get_window_extent().transformed(
            self.fig.dpi_scale_trans.inverted()
        )
        width, height = bbox.width, bbox.height
        self.fig.set_size_inches(width, height)

    def _init_plot(self):
        self.fig = plt.figure(
            figsize=(self.figure_size, self.figure_size),
            facecolor=self.style.figure_background_color.as_hex(),
            layout="constrained",
        )
        bounds = self._latlon_bounds()
        center_lon = (bounds[0] + bounds[1]) / 2
        self._center_lon = center_lon

        if self.projection in [
            Projection.ORTHOGRAPHIC,
            Projection.STEREOGRAPHIC,
            Projection.ZENITH,
        ]:
            # Calculate LST to shift RA DEC to be in line with current date and time
            lst = -(360.0 * self.timescale.gmst / 24.0 + self.lon) % 360.0
            self._proj = Projection.crs(self.projection, lon=lst, lat=self.lat)
        else:
            self._proj = Projection.crs(self.projection, center_lon)
        self._proj.threshold = 1000
        self.ax = plt.axes(projection=self._proj)

        if self._is_global_extent():
            if self.projection == Projection.ZENITH:
                theta = np.linspace(0, 2 * np.pi, 100)
                center, radius = [0.5, 0.5], 0.51
                verts = np.vstack([np.sin(theta), np.cos(theta)]).T
                circle = path.Path(verts * radius + center)
                extent = self.ax.get_extent(crs=self._proj)
                self.ax.set_extent((p / 3.75 for p in extent), crs=self._proj)
                self.ax.set_boundary(circle, transform=self.ax.transAxes)
            else:
                # this cartopy function works better for setting global extents
                self.ax.set_global()
        else:
            self.ax.set_extent(bounds, crs=self._plate_carree)

        self.ax.set_facecolor(self.style.background_color.as_hex())
        self._adjust_radec_minmax()

        self.logger.debug(f"Projection = {self.projection.value.upper()}")

        if self.projection == Projection.ZENITH:
            self._plot_border()
        else:
            # draw patch in axes coords, which are easier to work with
            # in cases like this cause they go from 0...1 in all plots
            self._background_clip_path = patches.Rectangle(
                (0, 0),
                width=1,
                height=1,
                facecolor=self.style.background_color.as_hex(),
                linewidth=0,
                fill=True,
                zorder=-2_000,
                transform=self.ax.transAxes,
            )
            self.ax.add_patch(self._background_clip_path)

        self._fit_to_ax()

    @use_style(LabelStyle, "info_text")
    def info(self, style: LabelStyle = None):
        """Plots info text in the lower left corner, including date/time and lat/lon.

        _Only available for ZENITH projections_

        Args:
            style: Styling of the info text. If None, then the plot's style definition will be used.
        """
        if not self.projection == Projection.ZENITH:
            raise NotImplementedError("info text only available for zenith projections")

        dt_str = self.dt.strftime("%m/%d/%Y @ %H:%M:%S") + " " + self.dt.tzname()
        info = f"{str(self.lat)}, {str(self.lon)}\n{dt_str}"
        self.ax.text(
            0.01,
            0.01,
            info,
            transform=self.ax.transAxes,
            **style.matplot_kwargs(self._size_multiplier * 1.36),
        )

    def _plot_border(self):
        """Plots circle border for Zenith projections"""
        border_font_kwargs = dict(
            fontsize=self.style.border_font_size * self._size_multiplier * 2.26,
            weight=self.style.border_font_weight,
            color=self.style.border_font_color.as_hex(),
            transform=self.ax.transAxes,
            zorder=5200,
        )
        self.ax.text(0.5, 0.98, "N", **border_font_kwargs)
        self.ax.text(0.9752, 0.5, "W", **border_font_kwargs)
        self.ax.text(0.00455, 0.5, "E", **border_font_kwargs)
        self.ax.text(0.5, 0.00456, "S", **border_font_kwargs)

        background_circle = patches.Circle(
            (0.5, 0.5),
            radius=0.475,
            fill=True,
            facecolor=self.style.background_color.as_hex(),
            edgecolor=self.style.border_line_color.as_hex(),
            linewidth=8 * self._size_multiplier,
            zorder=-1_000,
            transform=self.ax.transAxes,
        )
        self.ax.add_patch(background_circle)

        self._background_clip_path = background_circle

        border_circle = patches.Circle(
            (0.5, 0.5),
            radius=0.5,
            fill=False,
            edgecolor=self.style.border_bg_color.as_hex(),
            linewidth=90 * self._size_multiplier,
            zorder=1_000,
            transform=self.ax.transAxes,
        )
        self.ax.add_patch(border_circle)

        border_line_circle = patches.Circle(
            (0.5, 0.5),
            radius=0.51,
            fill=False,
            edgecolor=self.style.border_line_color.as_hex(),
            linewidth=8 * self._size_multiplier,
            zorder=1_200,
            transform=self.ax.transAxes,
        )
        self.ax.add_patch(border_line_circle)

        inner_border_line_circle = patches.Circle(
            (0.5, 0.5),
            radius=0.472,
            fill=False,
            edgecolor=self.style.border_line_color.as_hex(),
            linewidth=4 * self._size_multiplier,
            zorder=2_000,
            transform=self.ax.transAxes,
        )
        self.ax.add_patch(inner_border_line_circle)
