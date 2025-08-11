from typing import Callable

import numpy as np
from matplotlib.legend import Legend
from matplotlib.lines import Line2D

from starplot import callables
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

        if set_anchor and style.location.startswith("outside"):
            # display_to_figure_transform = self.fig.transFigure.inverted()
            display_to_axes_transform = self.ax.transAxes.inverted()
            extent = legend.get_window_extent(renderer=self.fig.canvas.get_renderer())
            min_x, min_y = display_to_axes_transform.transform(extent.min)
            max_x, max_y = display_to_axes_transform.transform(extent.max)

            a, b = self.ax.transAxes.transform((0, 0))

            px = 150  # every pixel here is really 2 pixels
            padding_x, _ = display_to_axes_transform.transform((a + px, b))

            width = max_x - min_x + padding_x
            # height = max_y - min_y
            # top_x, top_y = display_to_figure_transform.transform(self.ax.transAxes.transform((1, 1)))

            match style.location:
                # case LegendLocationEnum.OUTSIDE_TOP:
                #     bbox = (0.5, 1 + height)

                # case LegendLocationEnum.OUTSIDE_BOTTOM:
                #     bbox = (0.5, -1.12 * height)

                case LegendLocationEnum.OUTSIDE_TOP_RIGHT:
                    bbox = (1 + width, 1)

                case LegendLocationEnum.OUTSIDE_TOP_LEFT:
                    bbox = (-1 * width, 1)

                case LegendLocationEnum.OUTSIDE_BOTTOM_RIGHT:
                    bbox = (1 + width, 0)

                case LegendLocationEnum.OUTSIDE_BOTTOM_LEFT:
                    bbox = (-1 * width, 0)

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
            style: Styling of the legend. If None, then the plot's style (specified when creating the plot) will be used
        """
        if not self._legend_handles:
            return

        if self._legend:
            self._legend.remove()

        target = self.ax

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
        style: LegendStyle,
        title: str = "Star Magnitude",
        size_fn: Callable[[Star], float] = callables.size_by_magnitude,
        label_fn: Callable[float, str] = lambda m: str(m),
        start: float = -1,
        stop: float = 9,
        step: float = 1,
        add_to_legend: bool = False,
    ):
        target = self.ax

        if style.location.startswith("outside"):
            target = self.fig

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
