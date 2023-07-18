import warnings

from enum import Enum
from datetime import datetime

from adjustText import adjust_text as _adjust_text

import cartopy.crs as ccrs

from matplotlib import pyplot as plt, patheffects
import geopandas as gpd

from skyfield.api import Star

from starplot.constellations import labels as conlabels
from starplot.data import load, DataFiles
from starplot.models import SkyObject
from starplot.stars import get_star_data, hip_names
from starplot.styles import PlotStyle, GRAYSCALE, BLUE, MAP_BLUE


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


class StarPlot:
    def __init__(
        self,
        projection: Projection,
        lat: float = None,
        lon: float = None,
        dt: datetime = None,
        tz_identifier: str = None,
        limiting_magnitude: float = 6.0,
        limiting_magnitude_labels: float = 2.1,
        style: PlotStyle = GRAYSCALE,
        figure_size: int = 16,
        resolution: int = 2048,
        adjust_text: bool = True,
        *args,
        **kwargs,
    ):
        self.projection = projection
        self.limiting_magnitude = limiting_magnitude
        self.limiting_magnitude_labels = limiting_magnitude_labels
        self.style = style
        self.figure_size = figure_size
        self.resolution = resolution
        self.adjust_text = adjust_text

        self.labels = []
        self.text_border = patheffects.withStroke(
            linewidth=self.style.text_border_width,
            foreground=self.style.background_color.as_hex(),
        )
        self._size_multiplier = 64 / (self.resolution / self.figure_size)

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
            self.labels.append(label)

    def in_bounds(self, ra, dec) -> bool:
        raise NotImplementedError


class ZenithPlot(StarPlot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MapPlot(StarPlot):
    def __init__(
        self,
        ra_min: float,
        ra_max: float,
        dec_min: float,
        dec_max: float,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
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

    def _radec_extent(self):
        return (
            (self._extent[0] + 180) / 15,
            (self._extent[1] + 180) / 15,
            self._extent[2],
            self._extent[3],
        )

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
            color="#000",
            alpha=0.2,
            linewidth=2,
            ls="--",
            zorder=-100,
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

                extent = label.get_window_extent()

                if self.ax.contains_point(extent.p0) and self.ax.contains_point(
                    extent.p1
                ):
                    self.labels.append(label)
                else:
                    label.remove()

    def _plot_milky_way(self):
        mw = gpd.read_file(DataFiles.MILKY_WAY)
        mw.plot(
            ax=self.ax,
            **self.style.milky_way.matplot_kwargs,
            **self._plot_kwargs(),
        )

    def _plot_stars(self):
        stars = get_star_data()
        eph = load("de421_2001.bsp")
        earth = eph["earth"]
        t = load.timescale().utc(2023, 7, 2)
        nearby_stars_df = stars[
            (stars["magnitude"] <= self.limiting_magnitude)
            & (stars["ra_hours"] <= self.ra_max + 5)
            & (stars["ra_hours"] >= self.ra_min - 5)
            & (stars["dec_degrees"] <= self.dec_max + 10)
            & (stars["dec_degrees"] >= self.dec_min - 10)
        ]
        nearby_stars = Star.from_dataframe(nearby_stars_df)
        astrometric = earth.at(t).observe(nearby_stars)
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
                extent = label.get_window_extent()

                if self.ax.contains_point(extent.p0) and self.ax.contains_point(
                    extent.p1
                ):
                    self.labels.append(label)
                else:
                    label.remove()

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
