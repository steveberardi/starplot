from typing import Callable

import numpy as np
from matplotlib.legend import Legend
from matplotlib.lines import Line2D

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
    def _create_legend(self, handles, labels, title, style, set_anchor: bool = False):
        style_kwargs = style.matplot_kwargs(self.scale)

        target = self.ax

        if style.location.startswith("outside"):
            target = self.fig

        style_kwargs["borderaxespad"] = -1 * style.padding

        legend = Legend(
            target,
            handles=handles,
            labels=labels,
            title=title,
            **style_kwargs,
        )

        legend.set_zorder(
            # zorder is not a valid kwarg to legend(), so we have to set it afterwards
            style.zorder
        )
        legend.get_title().set_color(style.font_color.as_hex())

        if not set_anchor:
            return legend

        display_to_axes_transform = self.ax.transAxes.inverted()
        origin_x, origin_y = self.ax.transAxes.transform((0, 0))
        padding_x, padding_y = display_to_axes_transform.transform(
            (origin_x + style.padding_x / 2, origin_y + style.padding_y / 2)
        )

        if style.location.startswith("outside"):
            extent = legend.get_window_extent(renderer=self.fig.canvas.get_renderer())
            min_x, min_y = display_to_axes_transform.transform(extent.min)
            max_x, max_y = display_to_axes_transform.transform(extent.max)

            baseline, _ = display_to_axes_transform.transform(
                (origin_x + 200, origin_y + style.padding_y / 2)
            )

            padding_x += baseline
            width = max_x - min_x + padding_x
            # height = max_y - min_y
            # top_x, top_y = display_to_figure_transform.transform(self.ax.transAxes.transform((1, 1)))

            bbox = {
                LegendLocationEnum.OUTSIDE_TOP_RIGHT: (1 + width, 1 - padding_y),
                LegendLocationEnum.OUTSIDE_TOP_LEFT: (-1 * width, 1 - padding_y),
                LegendLocationEnum.OUTSIDE_BOTTOM_RIGHT: (1 + width, padding_y),
                LegendLocationEnum.OUTSIDE_BOTTOM_LEFT: (-1 * width, padding_y),
            }.get(style.location)

        else:
            bbox = {
                LegendLocationEnum.INSIDE_TOP_LEFT: (padding_x, 1 - padding_y),
                LegendLocationEnum.INSIDE_TOP_RIGHT: (1 - padding_x, 1 - padding_y),
                LegendLocationEnum.INSIDE_TOP: (0.5, 1 - padding_y),
                LegendLocationEnum.INSIDE_BOTTOM_LEFT: (padding_x, padding_y),
                LegendLocationEnum.INSIDE_BOTTOM_RIGHT: (1 - padding_x, padding_y),
                LegendLocationEnum.INSIDE_BOTTOM: (0.5, padding_y),
            }.get(style.location)

        legend.set_bbox_to_anchor(
            bbox=bbox,
            transform=self.ax.transAxes,
        )

        return legend

    @use_style(LegendStyle, "legend")
    def legend(self, title: str = "Legend", style: LegendStyle = None):
        """
        Plots the legend.

        If the legend is already plotted, then it'll be removed first and then plotted again. So, it's safe to call this function multiple times if you need to 'refresh' the legend.

        Args:
            title: Title of the legend, which will be plotted at the top
            style: Styling of the legend. If None, then the plot's style (specified when creating the plot) will be used
        """
        if not self._legend_handles:
            return

        if self._legend:
            self._legend.remove()

        target = self.ax

        title = translate(title, self.language)

        if style.location.startswith("outside"):
            target = self.fig

        legend = self._create_legend(
            handles=self._legend_handles.values(),
            labels=self._legend_handles.keys(),
            title=title,
            style=style,
            set_anchor=True,
        )

        target.add_artist(legend)

        self._legend = legend
        self._legend_target = target

    def _add_to_legend(self, legend):
        if not self._legend:
            self.legend()

        target = self._legend_target

        legend_base = self._legend.get_children()[0]
        legend_2 = legend.get_children()[0]

        # empty legend for padding
        empty = Legend(
            target,
            handles=[],
            labels=[],
            title="",
            # **style_kwargs,
        )

        # add empty legend for padding between legend and scale
        legend_base.get_children().extend(empty.get_children()[0].get_children())

        legend_base.get_children().extend(legend_2.get_children())

        legend_base.get_children().extend(empty.get_children()[0].get_children())

        # target.add_artist(self._legend)

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
                    size_fn(Star(ra=0, dec=0, magnitude=mag)) ** 0.5
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

        # for text in magnitude_scale.get_texts():
        #     text.set_ha("center") # horizontal alignment of text item
        #     text.set_x(-85) # x-position
        #     text.set_y(-90) # y-position

        # self.ax.add_artist(magnitude_scale)
