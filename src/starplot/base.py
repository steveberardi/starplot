from abc import ABC, abstractmethod
from datetime import datetime

from adjustText import adjust_text as _adjust_text
from matplotlib import pyplot as plt, patheffects
from pytz import timezone

from starplot.data import load
from starplot.models import SkyObject
from starplot.styles import PlotStyle, GRAYSCALE


class StarPlot(ABC):
    def __init__(
        self,
        dt: datetime = None,
        tz_identifier: str = None,
        limiting_magnitude: float = 6.0,
        limiting_magnitude_labels: float = 2.1,
        style: PlotStyle = GRAYSCALE,
        resolution: int = 2048,
        adjust_text: bool = True,
        ephemeris: str = "de421_2001.bsp",
        *args,
        **kwargs,
    ):
        px = 1 / plt.rcParams["figure.dpi"]  # pixel in inches

        self.limiting_magnitude = limiting_magnitude
        self.limiting_magnitude_labels = limiting_magnitude_labels
        self.style = style
        self.figure_size = resolution * px
        self.resolution = resolution
        self.adjust_text = adjust_text
        self.dt = dt or timezone("UTC").localize(datetime.now())
        self.ephemeris = ephemeris

        self.labels = []
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
            dpi=144,  # (self.resolution / self.figure_size * 1.28),
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
                **obj.style.marker.matplot_kwargs(
                    size_multiplier=self._size_multiplier
                ),
                **self._plot_kwargs(),
            )
            label = self.ax.text(
                ra,
                dec,
                obj.name,
                **obj.style.label.matplot_kwargs(size_multiplier=self._size_multiplier),
                **self._plot_kwargs(),
                path_effects=[self.text_border],
            )
            label.set_clip_on(True)
            self._maybe_remove_label(label)

    @abstractmethod
    def in_bounds(self, ra, dec) -> bool:
        raise NotImplementedError
