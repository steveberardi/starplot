import datetime
import warnings

from cartopy import crs as ccrs
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter, FixedLocator
from shapely.geometry.polygon import Polygon
from shapely import LineString, MultiLineString, MultiPolygon
from shapely.ops import unary_union, split
import geopandas as gpd
import numpy as np

from skyfield.api import Star

from starplot.base import StarPlot
from starplot.data import load, DataFiles, bayer, constellations, stars, dsos
from starplot.models import SkyObject
from starplot.projections import Projection
from starplot.styles import PlotStyle, PolygonStyle, MAP_BASE, MarkerSymbolEnum
from starplot.utils import lon_to_ra

# Silence noisy cartopy warnings
warnings.filterwarnings("ignore", module="cartopy")
warnings.filterwarnings("ignore", module="shapely")


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
        rasterize_stars: If True, then the stars will be rasterized when plotted, which can speed up exporting to SVG and reduce the file size but with a loss of image quality
        star_catalog: The catalog of stars to use: "hipparcos" or "tycho-1" -- Hipparcos is the default and has about 10x less stars than Tycho-1 but will also plot much faster
        dso_types: List of Deep Sky Objects (DSOs) types that will be plotted

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
        rasterize_stars: bool = False,
        star_catalog: stars.StarCatalog = stars.StarCatalog.HIPPARCOS,
        dso_types: list[dsos.DsoType] = dsos.DEFAULT_DSO_TYPES,
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
            rasterize_stars,
            *args,
            **kwargs,
        )

        if ra_min > ra_max:
            raise ValueError("ra_min must be less than ra_max")
        if dec_min > dec_max:
            raise ValueError("dec_min must be less than dec_max")

        self.projection = projection
        self.ra_min = ra_min
        self.ra_max = ra_max
        self.dec_min = dec_min
        self.dec_max = dec_max
        self.star_catalog = star_catalog
        self.dso_types = dso_types

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
            ra: Right ascension (0...24)
            dec: Declination (-90...90)

        Returns:
            True if the coordinate is in bounds, otherwise False

        """
        if self.ra_max < 24:
            return self.ra_min < ra < self.ra_max and self.dec_min < dec < self.dec_max
        else:
            return (
                ra > self.ra_min or ra < self.ra_max - 24
            ) and self.dec_min < dec < self.dec_max

    def _plot_polygon(self, points, style, **kwargs):
        super()._plot_polygon(points, style, transform=self._crs, **kwargs)

    def _latlon_bounds(self):
        # convert the RA/DEC bounds to lat/lon bounds
        return [
            -1 * self.ra_min * 15,
            -1 * self.ra_max * 15,
            self.dec_min,
            self.dec_max,
        ]

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

            if ra_min < 0 and ra_max < 0:
                ra_min += 24
                ra_max += 24

            self.ra_min = ra_min
            self.ra_max = ra_max

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

    def extent_bbox(self):
        # extent = self.ax.get_extent(crs=self._crs)
        # x0 = 360 + extent[0] * -1
        # x1 = 360 + extent[1] * -1

        # if x0 >= 360 and x1 >= 360:
        #     x0 -= 360
        #     x1 -= 360

        x0 = self.ra_min * 15
        x1 = self.ra_max * 15
        return (x0, self.dec_min, x1, self.dec_max)

    def _plot_dso_polygon(self, polygon, style):
        coords = list(zip(*polygon.exterior.coords.xy))
        coords = [(ra * -1, dec) for ra, dec in coords]
        p = Polygon(coords)

        poly_style = style.marker.to_polygon_style()
        pstyle = poly_style.matplot_kwargs(size_multiplier=self._size_multiplier)
        pstyle.pop("fill", None)
        self.ax.add_geometries([p], crs=self._plate_carree, **pstyle)

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

    def plot_dsos(self):
        ongc = gpd.read_file(
            DataFiles.ONGC.value,
            engine="pyogrio",
            use_arrow=True,
            bbox=self._extent_mask(),
        )

        dso_types = [dsos.ONGC_TYPE[dtype] for dtype in self.dso_types]
        nearby_dsos = ongc[ongc["Type"].isin(dso_types)]
        nearby_dsos = nearby_dsos.replace({np.nan: None})

        for n, d in nearby_dsos.iterrows():
            if d.ra_degrees is None or d.dec_degrees is None:
                continue

            ra = d.ra_degrees
            dec = d.dec_degrees

            name = d.Name
            dso_type = dsos.ONGC_TYPE_MAP[d.Type]
            style = self.style.get_dso_style(dso_type)
            maj_ax, min_ax, angle = d.MajAx, d.MinAx, d.PosAng
            legend_label = dsos.LEGEND_LABELS.get(dso_type) or dso_type
            magnitude = d["V-Mag"] or d["B-Mag"] or None
            magnitude = float(magnitude) if magnitude else None
            
            if (
                not style
                or not style.marker.visible
                or (magnitude is not None and magnitude > self.limiting_magnitude)
                # or (magnitude is None and "Nebula" in legend_label)
            ):
                continue

            geometry_types = d["geometry"].geom_type

            if "Polygon" in geometry_types and "MultiPolygon" not in geometry_types:
                self._plot_dso_polygon(d.geometry, style)

            elif "MultiPolygon" in geometry_types:
                for polygon in d.geometry.geoms:
                    self._plot_dso_polygon(polygon, style)

            elif maj_ax:
                # If object has a major axis then plot it's actual extent

                maj_ax_degrees = (maj_ax / 60) / 2

                if min_ax:
                    min_ax_degrees = (min_ax / 60) / 2
                else:
                    min_ax_degrees = maj_ax_degrees

                poly_style = style.marker.to_polygon_style()

                if style.marker.symbol == MarkerSymbolEnum.SQUARE:
                    self.plot_rectangle(
                        (ra / 15, dec),
                        min_ax_degrees * 2,
                        maj_ax_degrees * 2,
                        poly_style,
                        angle or 0,
                    )
                else:
                    self.plot_ellipse(
                        (ra / 15, dec),
                        min_ax_degrees * 2,
                        maj_ax_degrees * 2,
                        poly_style,
                        angle or 0,
                    )

                if style.label.visible:
                    self._plot_text(ra, dec, d.name)

            else:
                # If no major axis, then just plot as a marker
                obj = SkyObject(
                    name=name,
                    ra=ra / 15,
                    dec=dec,
                    style=style,
                )
                self.plot_object(obj)

            self._add_legend_handle_marker(legend_label, style.marker)

    def _plot_constellation_borders(self):
        if not self.style.constellation_borders.visible:
            return
        constellation_borders = self._read_geo_package(
            DataFiles.CONSTELLATION_BORDERS.value
        )

        if not constellation_borders.empty:
            constellation_borders.plot(
                ax=self.ax,
                **self.style.constellation_borders.matplot_kwargs(
                    size_multiplier=self._size_multiplier
                ),
                transform=self._plate_carree,
            )

    def plot_constellation_borders(self):
        """work in progress"""
        if not self.style.constellation_borders.visible:
            return

        constellation_borders = gpd.read_file(
            DataFiles.CONSTELLATIONS.value,
            engine="pyogrio",
            use_arrow=True,
            bbox=self.extent_bbox(),
        )

        if constellation_borders.empty:
            return

        geometries = []

        for i, c in constellation_borders.iterrows():
            polygon = c.geometry
            equinox = LineString([[0, 90], [0, -90]])
            polygons = list(split(polygon, equinox).geoms)

            for p in polygons:
                coords = list(zip(*p.exterior.coords.xy))
                # coords = [(ra * -1, dec) for ra, dec in coords]

                ls = LineString(coords)
                geometries.append(ls)

        mls = MultiLineString(geometries)
        geometries = unary_union(mls)

        style_kwargs = self.style.constellation_borders.matplot_kwargs(
            size_multiplier=self._size_multiplier
        )

        for ls in list(geometries.geoms):
            x, y = ls.xy
            self.ax.plot(
                list(x),
                list(y),
                **self._plot_kwargs(),
                **style_kwargs,
            )

    def plot_constellations(self):
        if not self.style.constellation.line.visible:
            return

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
        
        conline_hips = constellations.lines()
        style_kwargs = self.style.constellation.line.matplot_kwargs(
            size_multiplier=self._size_multiplier
        )

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
                    # print(f"{s1_ra} {s2_ra}")

                elif s2_ra - s1_ra > 60:
                    s1_ra += 360
                    # print(f"{c.id} : {s1_ra} {s2_ra}")

                s1_ra *= -1
                s2_ra *= -1
            
                # make lines straight
                # s1_ra, s1_dec = self._proj.transform_point(s1_ra, s1.dec_degrees, self._geodetic)
                # s2_ra, s2_dec = self._proj.transform_point(s2_ra, s2.dec_degrees, self._geodetic)

                self.ax.plot(
                    [s1_ra, s2_ra],
                    [s1_dec, s2_dec],
                    # **self._plot_kwargs(),
                    # transform=self._geodetic,
                    transform=transform,
                    **style_kwargs,
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

    def plot_milky_way(self, style: PolygonStyle = None):
        style = style or self.style.milky_way

        if not self.style.milky_way.visible:
            return

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

    def _plot_stars(self):
        stardata = stars.load(self.star_catalog)
        eph = load(self.ephemeris)
        earth = eph["earth"]

        self.stars_df = stardata

        ra_buffer = (self.ra_max - self.ra_min) / 4
        dec_buffer = (self.dec_max - self.dec_min) / 4

        nearby_stars_df = stardata[
            (stardata["magnitude"] <= self.limiting_magnitude)
            & (stardata["dec_degrees"] < self.dec_max + dec_buffer)
            & (stardata["dec_degrees"] > self.dec_min - dec_buffer)
        ]

        if self.ra_max < 24:
            nearby_stars_df = nearby_stars_df[
                (nearby_stars_df["ra_hours"] < self.ra_max + ra_buffer)
                & (nearby_stars_df["ra_hours"] > self.ra_min - ra_buffer)
            ]
        else:
            # handle wrapping
            nearby_stars_df = nearby_stars_df[
                (nearby_stars_df["ra_hours"] > self.ra_min - ra_buffer)
                | (nearby_stars_df["ra_hours"] < self.ra_max - 24 + ra_buffer)
            ]

        nearby_stars = Star.from_dataframe(nearby_stars_df)
        astrometric = earth.at(self.timescale).observe(nearby_stars)
        stars_ra, stars_dec, _ = astrometric.radec()

        sizes = []
        alphas = []

        # nearby_stars_df.sort_values("magnitude")

        for m in nearby_stars_df["magnitude"]:
            if m < 1.6:
                sizes.append((9 - m) ** 2.85 * self._star_size_multiplier)
                alphas.append(1)
            elif m < 4.6:
                sizes.append((8 - m) ** 2.92 * self._star_size_multiplier)
                alphas.append(1)
            elif m < 5.8:
                sizes.append((9 - m) ** 2.46 * self._star_size_multiplier)
                alphas.append(0.9)
            else:
                sizes.append(2.23 * self._star_size_multiplier)
                alphas.append((16 - m) * 0.09)

        # Plot Stars
        if self.style.star.marker.visible:
            self.ax.scatter(
                *self._prepare_coords(stars_ra.hours, stars_dec.degrees),
                sizes,
                marker=self.style.star.marker.symbol,
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

    def _fit_to_ax(self) -> None:
        bbox = self.ax.get_window_extent().transformed(
            self.fig.dpi_scale_trans.inverted()
        )
        width, height = bbox.width, bbox.height
        self.fig.set_size_inches(width, height)

    def _init_plot(self):
        self.fig = plt.figure(
            figsize=(self.figure_size, self.figure_size),
            facecolor=self.style.border_bg_color.as_hex(),
            layout="constrained",
        )
        bounds = self._latlon_bounds()
        center_lon = (bounds[0] + bounds[1]) / 2
        self._center_lon = center_lon

        self._proj = Projection.crs(self.projection, center_lon)
        self._proj.threshold = 1000
        self.ax = plt.axes(projection=self._proj)

        if self._is_global_extent():
            # this cartopy function works better for setting global extents
            self.ax.set_global()
        else:
            self.ax.set_extent(bounds, crs=self._plate_carree)

        self.ax.set_facecolor(self.style.background_color.as_hex())
        self._adjust_radec_minmax()

        self._plot_gridlines()
        self._plot_tick_marks()
        # self._plot_constellation_lines()
        self._plot_constellation_borders()
        self._plot_constellation_labels()
        self._plot_stars()

        # New
        self.plot_dsos()
        self.plot_milky_way()
        self.plot_constellations()
        # self.plot_constellation_borders()
        self.plot_ecliptic()
        self.plot_celestial_equator()
        self.plot_planets()
        self.plot_moon()

        self._fit_to_ax()

        self.refresh_legend()

        if self.adjust_text:
            self.adjust_labels()
