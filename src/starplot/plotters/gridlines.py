from collections.abc import Callable

from starplot import callables, geometry
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
        lon_label_fn: Callable[[float], str] = callables.rounded_degrees_label,
        lat_label_fn: Callable[[float], str] = callables.rounded_degrees_label,
        lon_label_locations: list[str] = None,
        lat_label_locations: list[str] = None,
    ):
        """
        Plots gridlines

        Args:
            style: Styling of the gridlines. If None, then the plot's style (specified when creating the plot) will be used
            labels: If True, then labels for each gridline will be plotted on the outside of the axes.
            lon_locations: List of longitude locations for the gridlines (in degrees, 0...360). Defaults to every 15 degrees.
            lat_locations: List of latitude locations for the gridlines (in degrees, -90...90). Defaults to every 10 degrees.
            lon_label_fn: Callable for creating labels of longitude gridlines.`
            lat_label_fn: Callable for creating labels of latitude gridlines.`
            lon_label_locations: Locations where labels will be plotted (options: `top` and/or `bottom`). Defaults to `['top', 'bottom']`
            lat_label_locations: Locations where labels will be plotted (options: `left` and/or `right`). Defaults to `['left', 'right']`
        """
        _labels = []
        lon_locations = lon_locations or [x for x in range(0, 375, 15)]
        lat_locations = lat_locations or [y for y in range(-80, 90, 10)]

        lon_label_locations = lon_label_locations or ["top", "bottom"]
        lat_label_locations = lat_label_locations or ["left", "right"]

        _, lat_min, _, lat_max = self.canvas.bounds

        # meridians are clipped to the plot's own dec extent (plus some padding) instead of
        # sweeping the full -90...90 range -- for azimuthal projections (e.g. StereoNorth),
        # dec values far from the visible extent project to extremely large coordinates, and
        # a single line containing such a point fails to render at all (silently dropped by
        # the cairo rendering backend), even for the portion that's within the visible area
        lat_padding = 10
        meridian_lat_min = max(-89.99999999, lat_min - lat_padding)
        meridian_lat_max = min(89.99999999, lat_max + lat_padding)

        with self.canvas.group(gid="gridlines"):
            for lon in lon_locations:
                coords = geometry.line_segment(
                    (lon, meridian_lat_min), (lon, meridian_lat_max), 0.5
                )
                self.line(coordinates=coords, style=style, skip_prepare=True)

                if labels:
                    _labels.append((coords, lon_label_fn(lon), lon_label_locations))

            for lat in lat_locations:
                coords = geometry.line_segment((0.00001, lat), (359.99999, lat), 0.5)
                self.line(coordinates=coords, style=style, skip_prepare=True)

                if labels:
                    _labels.append((coords, lat_label_fn(lat), lat_label_locations))

        if not labels:
            return

        border_style = PathStyle(line=LineStyle(stroke=None), label=style.label)
        self.canvas._axes_frame(
            border_style,
            labels=_labels,
            width_from_labels=True,
            label_gid="gridline-labels",
        )
