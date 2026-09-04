from collections.abc import Callable

from starplot import geometry
from starplot.profile import profile
from starplot.styles import (
    LineStyle,
    PathStyle,
)
from starplot.styles.helpers import use_style


class GridlinesPlotterMixin:
    @profile
    @use_style(PathStyle, "gridlines")
    def gridlines(
        self,
        style: PathStyle = None,
        labels: bool = True,
        lon_locations: list[float] = None,
        lat_locations: list[float] = None,
        lon_formatter_fn: Callable[[float], str] = None,
        lat_formatter_fn: Callable[[float], str] = None,
    ):
        """
        Plots gridlines

        Args:
            style: Styling of the gridlines. If None, then the plot's style (specified when creating the plot) will be used
            labels: If True, then labels for each gridline will be plotted on the outside of the axes.
            lon_locations: List of longitude locations for the gridlines (in degrees, 0...360). Defaults to every 15 degrees.
            lat_locations: List of latitude locations for the gridlines (in degrees, -90...90). Defaults to every 10 degrees.
            lon_formatter_fn: Callable for creating labels of longitude gridlines. Defaults to `lambda lon: f"{round(lon)}\u00b0 "`
            lat_formatter_fn: Callable for creating labels of latitude gridlines. Defaults to `lambda lat: f"{round(lat)}\u00b0 "`
        """

        _labels = []

        lon_formatter_fn_default = lambda lon: f"{round(lon)}\u00b0 "
        lat_formatter_fn_default = lambda lat: f"{round(lat)}\u00b0 "

        _lon_formatter_fn = lon_formatter_fn or lon_formatter_fn_default
        _lat_formatter_fn = lat_formatter_fn or lat_formatter_fn_default

        lon_locations = lon_locations or [x for x in range(0, 375, 15)]
        lat_locations = lat_locations or [y for y in range(-80, 90, 10)]

        # meridians are clipped to the plot's own dec extent (plus some padding) instead of
        # sweeping the full -90...90 range -- for azimuthal projections (e.g. StereoNorth),
        # dec values far from the visible extent project to extremely large coordinates, and
        # a single line containing such a point fails to render at all (silently dropped by
        # the cairo rendering backend), even for the portion that's within the visible area
        lat_padding = 10
        meridian_lat_min = max(-89.99999999, self.dec_min - lat_padding)
        meridian_lat_max = min(89.99999999, self.dec_max + lat_padding)

        with self.canvas.group(gid="gridlines"):
            for lon in lon_locations:
                coords = geometry.line_segment(
                    (lon, meridian_lat_min), (lon, meridian_lat_max), 0.5
                )
                self.line(coordinates=coords, style=style, skip_prepare=True)

                if labels:
                    _labels.append((coords, _lon_formatter_fn(lon), ("top", "bottom")))

            for lat in lat_locations:
                coords = geometry.line_segment((0.00001, lat), (359.99999, lat), 0.5)
                self.line(coordinates=coords, style=style, skip_prepare=True)

                if labels:
                    _labels.append((coords, _lat_formatter_fn(lat), ("left", "right")))

        if not labels:
            return

        border_style = PathStyle(line=LineStyle(stroke=None), label=style.label)
        self.canvas._axes_frame(
            border_style,
            labels=_labels,
            width_from_labels=True,
            label_gid="gridline-labels",
        )
