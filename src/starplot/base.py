from abc import ABC, abstractmethod
from datetime import datetime

from adjustText import adjust_text as _adjust_text
from matplotlib import pyplot as plt, patheffects, transforms
from matplotlib.lines import Line2D
from pytz import timezone

from starplot.data import load
from starplot.models import SkyObject
from starplot.planets import get_planet_positions
from starplot.styles import PlotStyle, BASE, MarkerStyle, LegendLocationEnum


class StarPlot(ABC):
    def __init__(
        self,
        dt: datetime = None,
        limiting_magnitude: float = 6.0,
        limiting_magnitude_labels: float = 2.1,
        ephemeris: str = "de421_2001.bsp",
        style: PlotStyle = BASE,
        resolution: int = 2048,
        hide_colliding_labels: bool = True,
        adjust_text: bool = False,
        *args,
        **kwargs,
    ):
        px = 1 / plt.rcParams["figure.dpi"]  # pixel in inches

        self.limiting_magnitude = limiting_magnitude
        self.limiting_magnitude_labels = limiting_magnitude_labels
        self.style = style
        self.figure_size = resolution * px
        self.resolution = resolution
        self.hide_colliding_labels = hide_colliding_labels
        self.adjust_text = adjust_text

        self.dt = dt or timezone("UTC").localize(datetime.now())
        self.ephemeris = ephemeris

        self.labels = []
        self._labels_extents = []
        self._legend_handles = {}
        self.legend = None
        self.text_border = patheffects.withStroke(
            linewidth=self.style.text_border_width,
            foreground=self.style.background_color.as_hex(),
        )
        self._size_multiplier = self.resolution / 3000

        self.timescale = load.timescale().from_datetime(self.dt)

    def _plot_kwargs(self) -> dict:
        return {}

    def _prepare_coords(self, ra, dec) -> (float, float):
        return ra, dec

    def _is_label_collision(self, extent) -> bool:
        for e in self._labels_extents:
            if transforms.Bbox.intersection(e, extent):
                return True
        return False

    def _maybe_remove_label(self, label) -> None:
        extent = label.get_window_extent(renderer=self.fig.canvas.get_renderer())
        ax_extent = self.ax.get_window_extent()

        if transforms.Bbox.intersection(ax_extent, extent) and not (
            self.hide_colliding_labels and self._is_label_collision(extent)
        ):
            self.labels.append(label)
            self._labels_extents.append(extent)
        else:
            label.remove()

    def _add_legend_handle_marker(self, label: str, style: MarkerStyle):
        if label not in self._legend_handles:
            self._legend_handles[label] = Line2D(
                [],
                [],
                **style.matplot_kwargs(size_multiplier=self._size_multiplier),
                **self._plot_kwargs(),
                linestyle="None",
                label=label,
            )

    def refresh_legend(self):
        """Redraws the legend.

        This is useful if you want to include objects in the legend that were plotted AFTER creating the plot (via `plot_object`)
        """
        if not self.style.legend.visible or not self._legend_handles:
            return

        if self.legend is not None:
            self.legend.remove()

        if self.style.legend.location in [
            LegendLocationEnum.OUTSIDE_BOTTOM,
            LegendLocationEnum.OUTSIDE_TOP,
        ]:
            # to plot legends outside the map area, you have to target the figure
            target = self.fig
        else:
            target = self.ax

        self.legend = target.legend(
            handles=self._legend_handles.values(),
            **self.style.legend.matplot_kwargs(size_multiplier=self._size_multiplier),
        )

    def adjust_labels(self) -> None:
        """Adjust all the labels to avoid overlapping."""
        _adjust_text(self.labels, ax=self.ax, ensure_inside_axes=False)

    def close_fig(self) -> None:
        """Closes the underlying matplotlib figure."""
        if self.fig:
            plt.close(self.fig)

    def export(self, filename: str, format: str = "png", padding: float = 0, **kwargs):
        """Exports the plot to an image file.

        Args:
            filename: Filename of exported file
            format: Format of file: "png" or "svg"
            padding: Padding (in inches) around the image
            **kwargs: Any keyword arguments to pass through to matplotlib's `savefig` method

        """
        self.fig.savefig(
            filename,
            format=format,
            bbox_inches="tight",
            pad_inches=padding,
            dpi=144,  # (self.resolution / self.figure_size * 1.28),
            **kwargs,
        )

    def draw_reticle(
        self, ra: float, dec: float, size: int = 6, color: str = "red"
    ) -> None:
        """Plots a basic reticle on the map.

        Args:
            ra: Right ascension of the reticle's center
            dec: Declination of the reticle's center
            size: Relative size of the reticle
            color: Color of the reticle ([Matplotlib format](https://matplotlib.org/stable/users/explain/colors/colors.html#colors-def))

        """

        # Plot as a marker to avoid projection distortion
        self.ax.plot(
            *self._prepare_coords(ra, dec),
            marker="o",
            markersize=size,
            color=color,
            zorder=1024,
            **self._plot_kwargs(),
        )
        self.ax.plot(
            *self._prepare_coords(ra, dec),
            marker="o",
            markerfacecolor=None,
            markersize=size * 5,
            color=color,
            ls="dashed",
            zorder=1024,
            fillstyle="none",
            **self._plot_kwargs(),
        )

    def plot_object(self, obj: SkyObject) -> None:
        """Plots an object (see SkyObject for details).

        Args:
            obj: The object to plot

        """
        x, y = self._prepare_coords(obj.ra, obj.dec)

        if self.in_bounds(obj.ra, obj.dec):
            self.ax.plot(
                x,
                y,
                **obj.style.marker.matplot_kwargs(
                    size_multiplier=self._size_multiplier
                ),
                **self._plot_kwargs(),
                linestyle="None",
            )

            if obj.legend_label is not None:
                self._add_legend_handle_marker(obj.legend_label, obj.style.marker)

            if obj.style.label.visible:
                label = self.ax.text(
                    x,
                    y,
                    obj.name,
                    **obj.style.label.matplot_kwargs(
                        size_multiplier=self._size_multiplier
                    ),
                    **self._plot_kwargs(),
                    path_effects=[self.text_border],
                )
                label.set_clip_on(True)
                self._maybe_remove_label(label)

    def _plot_text(self, ra: float, dec: float, text: str, *args, **kwargs) -> None:
        x, y = self._prepare_coords(ra, dec)
        kwargs["path_effects"] = kwargs.get("path_effects") or [self.text_border]
        label = self.ax.text(
            x,
            y,
            text,
            *args,
            **kwargs,
            **self._plot_kwargs(),
        )
        label.set_clip_on(True)
        self._maybe_remove_label(label)

    def _plot_planets(self):
        if not self.style.planets.marker.visible:
            return

        planets = get_planet_positions(self.timescale, ephemeris=self.ephemeris)

        for name, pos in planets.items():
            ra, dec = pos

            if self.in_bounds(ra, dec):
                self._add_legend_handle_marker("Planet", self.style.planets.marker)

            obj = SkyObject(
                name=name.upper(),
                ra=ra,
                dec=dec,
                style=self.style.planets,
            )
            self.plot_object(obj)

    def _plot_moon(self):
        if not self.style.moon.marker.visible:
            return

        eph = load(self.ephemeris)
        earth, moon = eph["earth"], eph["moon"]

        astrometric = earth.at(self.timescale).observe(moon)
        ra, dec, _ = astrometric.radec()

        obj = SkyObject(
            name="MOON",
            ra=ra.hours,
            dec=dec.degrees,
            style=self.style.moon,
            legend_label="Moon",
        )
        self.plot_object(obj)

    @abstractmethod
    def in_bounds(self, ra: float, dec: float) -> bool:
        """Determine if a coordinate is within the bounds of the plot.

        Args:
            ra: Right ascension
            dec: Declination

        Returns:
            bool: True if the coordinate is in bounds, otherwise False

        """
        raise NotImplementedError
