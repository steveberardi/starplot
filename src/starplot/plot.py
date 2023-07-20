import warnings

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime

from adjustText import adjust_text as _adjust_text

import cartopy.crs as ccrs

from matplotlib import pyplot as plt, patheffects
from matplotlib.collections import LineCollection
import geopandas as gpd
from pytz import timezone

from skyfield.api import Star, wgs84
from skyfield.positionlib import position_of_radec
from skyfield.projections import build_stereographic_projection

from starplot.constellations import (
    create_projected_constellation_lines,
    labels as conlabels,
)
from starplot.data import load, DataFiles
from starplot.models import SkyObject
from starplot.stars import get_star_data, hip_names
from starplot.styles import PlotStyle, GRAYSCALE, BLUE, MAP_BLUE
from starplot.utils import in_circle


# Silence noisy cartopy warnings
warnings.filterwarnings("ignore", module="cartopy")


class Projection(str, Enum):
    STEREO_ZENITH = "stereo_zenith"
    STEREO_NORTH = "stereo_north"
    STEREO_SOUTH = "stereo_south"
    MERCATOR = "mercator"

    @staticmethod
    def crs(projection):
        return {
            Projection.STEREO_NORTH: ccrs.NorthPolarStereo(),
            Projection.STEREO_SOUTH: ccrs.SouthPolarStereo(),
            Projection.MERCATOR: ccrs.PlateCarree(-180),
        }.get(projection)


class StarPlot(ABC):
    def __init__(
        self,
        dt: datetime = None,
        # tz_identifier: str = None,
        limiting_magnitude: float = 6.0,
        limiting_magnitude_labels: float = 2.1,
        style: PlotStyle = GRAYSCALE,
        figure_size: int = 16,
        resolution: int = 2048,
        adjust_text: bool = True,
        ephemeris: str = "de421_2001.bsp",
        *args,
        **kwargs,
    ):
        self.limiting_magnitude = limiting_magnitude
        self.limiting_magnitude_labels = limiting_magnitude_labels
        self.style = style
        self.figure_size = figure_size
        self.resolution = resolution
        self.adjust_text = adjust_text
        self.dt = dt or timezone("UTC").localize(datetime.now())
        self.ephemeris = ephemeris

        self.labels = []
        self.text_border = patheffects.withStroke(
            linewidth=self.style.text_border_width,
            foreground=self.style.background_color.as_hex(),
        )
        self._size_multiplier = 64 / (self.resolution / self.figure_size)

        self.timescale = load.timescale().from_datetime(self.dt)

        # if projection == Projection.STEREO_ZENITH:
        #     if not all([lat, lon, dt, tz_identifier]):
        #         raise ValueError(
        #             "Missing required kwarg for 'stereo_zenith' projection: lat, lon, dt, and tz_identifier are required"
        #         )
        # else:
        #     if not all([ra_min, ra_max, dec_min, dec_max]):
        #         raise ValueError(
        #             f"Missing required kwarg for '{projection.name}' projection: ra_min, ra_max, dec_min, dec_max are required"
        #         )

    def _plot_kwargs(self) -> dict:
        return {}

    def _prepare_coords(self, ra, dec) -> (float, float):
        return ra, dec

    def _maybe_remove_label(self, label):
        extent = label.get_window_extent(renderer=self.fig.canvas.get_renderer())

        if self.ax.contains_point(extent.p0) and self.ax.contains_point(extent.p1):
            self.labels.append(label)
        else:
            label.remove()

    def adjust_labels(self) -> None:
        _adjust_text(self.labels, ax=self.ax, ensure_inside_axes=False)

    def close_fig(self) -> None:
        if self.fig:
            plt.close(self.fig)

    def export(self, filename: str, format: str = "png"):
        self.fig.savefig(
            filename,
            format=format,
            bbox_inches="tight",
            pad_inches=0,
            dpi=(self.resolution / self.figure_size * 1.28),
        )

    def draw_reticle(self, ra, dec) -> None:
        # Plot as a marker to avoid projection distortion
        self.ax.plot(
            *self._prepare_coords(ra, dec),
            marker="o",
            markersize=6,
            color="red",
            zorder=1024,
            **self._plot_kwargs(),
        )
        self.ax.plot(
            *self._prepare_coords(ra, dec),
            marker="o",
            markerfacecolor=None,
            markersize=28,
            color="red",
            ls="dashed",
            zorder=1024,
            fillstyle="none",
            **self._plot_kwargs(),
        )

    def plot_object(self, obj: SkyObject):
        ra, dec = self._prepare_coords(obj.ra, obj.dec)

        if self.in_bounds(obj.ra, obj.dec):
            self.ax.plot(
                ra,
                dec,
                **obj.style.marker.matplot_kwargs,
                **self._plot_kwargs(),
            )
            label = self.ax.text(
                ra,
                dec,
                obj.name,
                **obj.style.label.matplot_kwargs,
                **self._plot_kwargs(),
                path_effects=[self.text_border],
            )
            label.set_clip_on(True)
            self._maybe_remove_label(label)

    @abstractmethod
    def in_bounds(self, ra, dec) -> bool:
        raise NotImplementedError


class ZenithPlot(StarPlot):
    def __init__(self, lat: float = None, lon: float = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lat = lat
        self.lon = lon

        self._calc_position()
        self.project_fn = build_stereographic_projection(self.position)

        self._init_plot()
    
    def in_bounds(self, ra, dec) -> bool:
        return False
    
    def _calc_position(self):
        loc = wgs84.latlon(self.lat, self.lon).at(self.timescale)
        self.position = loc.from_altaz(alt_degrees=90, az_degrees=0)
        
    def _plot_constellation_lines(self):
        constellations = LineCollection(
            create_projected_constellation_lines(self._stardata),
            **self.style.constellation.line.matplot_kwargs,
        )
        self._plotted_conlines = self.ax.add_collection(constellations)

    def _plot_constellation_labels(self):
        for con in conlabels:
            fullname, ra, dec = conlabels.get(con)
            x, y = self.project_fn(position_of_radec(ra, dec))

            if in_circle(x, y):
                label = self.ax.text(
                    x,
                    y,
                    fullname.upper(),
                    path_effects=[self.text_border],
                    **self.style.constellation.label.matplot_kwargs,
                )
                self._maybe_remove_label(label)
    
    def _plot_stars(self):
        stardata = get_star_data(self.limiting_magnitude)
        self._stardata = stardata

        eph = load(self.ephemeris)
        earth = eph["earth"]

        # project stars to stereographic plot
        star_positions = earth.at(self.timescale).observe(Star.from_dataframe(stardata))
        stardata["x"], stardata["y"] = self.project_fn(star_positions)

        # filter stars by limiting magnitude
        bright_stars = stardata.magnitude <= self.limiting_magnitude

        # calculate size of each star based on magnitude
        sizes = []
        for m in stardata["magnitude"][bright_stars]:
            if m < 2:
                sizes.append((6 - m) ** 2.26)
            else:
                sizes.append((1 + self.limiting_magnitude - m) ** 2)
        
        # Draw stars
        self._plotted_stars = self.ax.scatter(
            stardata["x"][bright_stars],
            stardata["y"][bright_stars],
            sizes,
            color=self.style.star.marker.color.as_hex(),
        )

        starpos_x = []
        starpos_y = []

        # Plot star names
        for i, s in stardata[bright_stars].iterrows():
            if (
                in_circle(s["x"], s["y"])
                and i in hip_names
                and s["magnitude"] < self.limiting_magnitude_labels
            ):
                label = self.ax.text(
                    s["x"] + 0.00984,
                    s["y"] - 0.006,
                    hip_names[i],
                    **self.style.star.label.matplot_kwargs,
                    ha="left",
                    va="top",
                    path_effects=[self.text_border],
                )
                label.set_alpha(self.style.star.label.font_alpha)
                label.set_clip_on(True)
                self._maybe_remove_label(label)

                starpos_x.append(s["x"])
                starpos_y.append(s["y"])
    
    def _plot_border(self):
        # Plot border text
        border_font_kwargs = dict(
            fontsize=self.style.border_font_size,
            weight=self.style.border_font_weight,
            color=self.style.border_font_color.as_hex(),
        )
        self.ax.text(0, 1.009, "N", **border_font_kwargs)
        self.ax.text(1.003, 0, "W", **border_font_kwargs)
        self.ax.text(-1.042, 0, "E", **border_font_kwargs)
        self.ax.text(0, -1.045, "S", **border_font_kwargs)

        # Background Circle
        background_circle = plt.Circle(
            (0, 0),
            facecolor=self.style.background_color.as_hex(),
            radius=1.0,
            linewidth=0,
            fill=True,
            zorder=-100,
        )
        self.ax.add_patch(background_circle)

        # clip stars outside background circle
        self._plotted_stars.set_clip_path(background_circle)
        self._plotted_conlines.set_clip_path(background_circle)

        # Border Circles
        inner_border = plt.Circle(
            (0, 0),
            radius=1.0,
            linewidth=2,
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
            linewidth=4,
            edgecolor=self.style.border_line_color.as_hex(),
            fill=True,
            zorder=-200,
        )
        self.ax.add_patch(outer_border)

    
    def _init_plot(self):
        self.fig = plt.figure(figsize=(self.figure_size, self.figure_size))
        self.ax = plt.axes()

        self.ax.set_xlim(-1.1, 1.1)
        self.ax.set_ylim(-1.1, 1.1)
        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.set_visible(False)
        self.ax.set_aspect(1.0)
        plt.axis("off")
        
        self._plot_stars()
        self._plot_constellation_lines()
        self._plot_constellation_labels()
        self._plot_border()
        
        if self.adjust_text:
            self.adjust_labels()


class MapPlot(StarPlot):
    def __init__(
        self,
        projection: Projection,
        ra_min: float,
        ra_max: float,
        dec_min: float,
        dec_max: float,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.projection = projection
        self.ra_min = ra_min
        self.ra_max = ra_max
        self.dec_min = dec_min
        self.dec_max = dec_max
        self._init_plot()

    def _plot_kwargs(self) -> dict:
        return dict(transform=ccrs.PlateCarree())

    def _prepare_coords(self, ra, dec) -> (float, float):
        return (ra * 15 - 360) * -1, dec

    def in_bounds(self, ra, dec) -> bool:
        return self.ra_min < ra < self.ra_max and self.dec_min < dec < self.dec_max

    def _latlon_bounds(self):
        return [
            self.ra_min * 15 - 180,
            self.ra_max * 15 - 180,
            self.dec_min,
            self.dec_max,
        ]

    def _adjust_radec_minmax(self):
        extent = self.ax.get_extent(crs=ccrs.PlateCarree())
        self.ra_min = (extent[0] + 180) / 15
        self.ra_max = (extent[1] + 180) / 15
        self.dec_min = extent[2]
        self.dec_max = extent[3]

    def _plot_constellation_lines(self):
        constellation_lines = gpd.read_file(DataFiles.CONSTELLATION_LINES)
        constellation_lines.plot(
            ax=self.ax,
            **self.style.constellation.line.matplot_kwargs,
            **self._plot_kwargs(),
        )

    def _plot_constellation_borders(self):
        constellation_borders = gpd.read_file(DataFiles.CONSTELLATION_BORDERS)
        constellation_borders.plot(
            ax=self.ax,
            **self.style.constellation_borders.matplot_kwargs,
            **self._plot_kwargs(),
        )

    def _plot_constellation_labels(self):
        for con in conlabels:
            fullname, ra, dec = conlabels.get(con)
            if self.in_bounds(ra, dec):
                label = self.ax.text(
                    *self._prepare_coords(ra, dec),
                    con.upper(),
                    **self.style.constellation.label.matplot_kwargs,
                    **self._plot_kwargs(),
                )
                label.set_clip_on(True)
                self._maybe_remove_label(label)

    def _plot_milky_way(self):
        mw = gpd.read_file(DataFiles.MILKY_WAY)
        mw.plot(
            ax=self.ax,
            **self.style.milky_way.matplot_kwargs,
            **self._plot_kwargs(),
        )

    def _plot_stars(self):
        stars = get_star_data()
        eph = load(self.ephemeris)
        earth = eph["earth"]
        nearby_stars_df = stars[
            (stars["magnitude"] <= self.limiting_magnitude)
            & (stars["ra_hours"] < self.ra_max + 5)
            & (stars["ra_hours"] > self.ra_min - 5)
            & (stars["dec_degrees"] < self.dec_max + 10)
            & (stars["dec_degrees"] > self.dec_min - 10)
        ]
        nearby_stars = Star.from_dataframe(nearby_stars_df)
        astrometric = earth.at(self.timescale).observe(nearby_stars)
        stars_ra, stars_dec, _ = astrometric.radec()

        sizes = []
        for m in nearby_stars_df["magnitude"]:
            if m < 4.6:
                sizes.append((8 - m) ** 2 * self._size_multiplier)
            else:
                sizes.append(0.75 * self._size_multiplier)

        # Plot Stars
        self.ax.scatter(
            *self._prepare_coords(stars_ra.hours, stars_dec.degrees),
            sizes,
            zorder=100,
            color=self.style.star.marker.color.as_hex(),
            **self._plot_kwargs(),
        )

        # Plot star names
        for i, s in nearby_stars_df.iterrows():
            if (
                i in hip_names
                and s["magnitude"] < self.limiting_magnitude
                # and self.in_bounds(s["ra_hours"], s["dec_degrees"])
            ):
                label = self.ax.text(
                    *self._prepare_coords(s["ra_hours"], s["dec_degrees"]),
                    hip_names[i],
                    ha="left",
                    va="top",
                    **self.style.star.label.matplot_kwargs,
                    **self._plot_kwargs(),
                )
                label.set_clip_on(True)
                self._maybe_remove_label(label)

    def _init_plot(self):
        self.fig = plt.figure(figsize=(self.figure_size, self.figure_size))
        self.ax = plt.axes(projection=Projection.crs(self.projection))
        self.ax.set_extent(self._latlon_bounds(), crs=ccrs.PlateCarree())
        self._adjust_radec_minmax()

        gridlines = self.ax.gridlines(draw_labels=False)
        gridlines.top_labels = False
        gridlines.right_labels = False

        self._plot_constellation_lines()
        self._plot_constellation_borders()
        self._plot_constellation_labels()
        self._plot_milky_way()
        self._plot_stars()

        # print(self.ax.patch.get_extents())
        # print(self.ax.get_window_extent())
        # print(self.ax.get_position())
        # self._extent = self.ax.get_extent(crs=ccrs.PlateCarree())

        if self.adjust_text:
            self.adjust_labels()
