import math
from typing import Callable

import numpy as np

from starplot import callables
from starplot.data.translations import translate
from starplot.models.star import Star
from starplot.styles import (
    MarkerStyle,
    LegendLocationEnum,
    LegendStyle,
)
from starplot.styles.helpers import use_style


class LegendPlotterMixin:
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._legend_handles = {}

    def _add_legend_handle_marker(self, label: str, style: MarkerStyle):
        self._legend_handles[label] = (style.model_copy(), None)

    @use_style(LegendStyle, "legend")
    def legend(
        self,
        title: str = "Legend",
        style: LegendStyle = None,
        magnitude_scale: bool = False,
        magnitude_scale_title: str = "Star Magnitude",
        magnitude_start: float = None,
        magnitude_stop: float = None,
        magnitude_step: float = 1,
        magnitude_size_fn: Callable = None,
        magnitude_label_fn: Callable = None,
    ):
        """
        Plots the legend.

        If the legend is already plotted, then it'll be removed first and then plotted again. So, it's safe to call this function multiple times if you need to 'refresh' the legend.

        Args:
            title: Title of the legend, which will be plotted at the top
            style: Styling of the legend. If None, then the plot's style (specified when creating the plot) will be used
        """
        if not self._legend_handles:
            return

        title = translate(title, self.language)

        sections = [(title, self._legend_handles)]

        if magnitude_scale:
            magnitudes = {}
            min_mag, max_mag = self.magnitude_range
            magnitude_start = magnitude_start or math.floor(min_mag)
            magnitude_stop = magnitude_stop or math.ceil(max_mag)
            magnitude_size_fn = magnitude_size_fn or self._last_used_size_fn
            magnitude_label_fn = magnitude_label_fn or (lambda m: str(m))

            for mag in np.arange(magnitude_start, magnitude_stop, magnitude_step):
                label = magnitude_label_fn(mag)
                size = magnitude_size_fn(
                    Star(pk=1, ra=0, dec=0, magnitude=mag, geometry=None)
                )
                magnitudes[label] = (self.style.star.marker, size)

            sections.append((magnitude_scale_title, magnitudes))

        self.canvas.legend(
            sections=sections,
            style=style,
        )

    @use_style(LegendStyle, "legend")
    def star_magnitude_scale(
        self,
        title: str = "Star Magnitude",
        style: LegendStyle = None,
        size_fn: Callable[[Star], float] = callables.size_by_magnitude,
        label_fn: Callable[float, str] = lambda m: str(m),
        start: float = -1,
        stop: float = 9,
        step: float = 1,
        add_to_legend: bool = False,
    ):
        """
        Plots a magnitude scale for stars.

        !!! example "Experimental"

            This is currently an "experimental" feature, which means it's likely to be changed and improved in upcoming versions of Starplot.
            It also means the feature likely has limitations.

            **Help us improve this feature by submitting feedback on [GitHub (open an issue)](https://github.com/steveberardi/starplot/issues) or chat with us on [Discord](https://discord.gg/WewJJjshFu). Thanks!**

        !!! note "Current Limitations"
            - Only supports size functions that determine size based on magnitude only
            - Only supports default marker for stars (point)
            - Labels can only be plotted to the right of the marker
            - Does not automatically determine the magnitude range of the stars you already plotted

        Args:
            title: Title of the legend, which will be plotted at the top
            style: Styling of the magnitude scale. If None, then the plot's `legend` style will be used
            size_fn: Size function for the star markers
            label_fn: Function to determine the label for each magnitude
            start: Starting magnitude
            stop: Stop point (exclusive)
            step: Step-size of each scale entry (i.e. how much to increment each step)
            add_to_legend: If True, the scale will be added to the bottom of the legend (and if the legend isn't already plotted, then it'll plot the legend)
        """

        """
        TODO (for svg):

        - maybe include this in the legend function? e.g. kwarg for include_star_magnitude_scale
        - use last used size function by default
        - use magnitude range of already plotted by default
        - support all markers

        """
        target = self.ax

        if style.location.startswith("outside"):
            target = self.fig

        title = translate(title, self.language)

        def scale(
            size_fn,
            style: MarkerStyle,
            label_fn,
            start: float,
            stop: float,
            step: float = 1,
        ):
            for mag in np.arange(start, stop, step):
                s = style.matplot_kwargs()
                s["markersize"] = (
                    size_fn(Star(pk=1, ra=0, dec=0, magnitude=mag, geometry=None))
                    ** 0.5
                ) * self.scale
                label = label_fn(mag)
                yield Line2D(
                    [],
                    [],
                    **s,
                    linestyle="None",
                    label=label,
                )

        handles = [
            h
            for h in scale(
                size_fn=size_fn,
                style=self.style.star.marker,
                label_fn=label_fn,
                start=start,
                stop=stop,
                step=step,
            )
        ]
        labels = [str(m) for m in np.arange(start, stop, step)]

        scale = self._create_legend(
            handles=handles,
            labels=labels,
            title=title,
            style=style,
            set_anchor=True if not add_to_legend else False,
        )

        if add_to_legend:
            self._add_to_legend(scale)
        else:
            target.add_artist(scale)
