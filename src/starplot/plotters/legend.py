import math
from typing import Callable

import numpy as np

from starplot.data.translations import translate
from starplot.models.star import Star
from starplot.styles import (
    MarkerStyle,
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

        !!! note "Star Magnitude Scale - Limitations"
            - Only supports size functions that determine size based on magnitude
            - Does not automatically determine the magnitude range of the stars you already plotted

        Args:
            title: Title of the legend, which will be plotted at the top
            style: Styling of the legend. If None, then the plot's style (specified when creating the plot) will be used
            magnitude_scale: If True, a star magnitude scale will also be plotted
            magnitude_scale_title: Title of the star magnitude section
            magnitude_start: Magnitude to start at in the magnitude scale
            magnitude_stop: Magnitude to stop at in the magnitude scale
            magnitude_step: Step size for magnitudes in the scale
            magnitude_size_fn: Size function for the star magnitudes. Defaults to the last used size function when calling `stars()`
            magnitude_label_fn: Function for determining the label for each magnitude in the scale. The function should take a single parameter and return a string. Default is `lambda m: str(m)`
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
