from typing import Mapping

import geopandas as gpd
import numpy as np

from starplot.data import DataFiles
from starplot.data.dsos import (
    DsoType,
    DEFAULT_DSO_TYPES,
    ONGC_TYPE,
    ONGC_TYPE_MAP,
    DSO_LEGEND_LABELS,
    DSO_LABELS_DEFAULT,
    DsoLabelMaker,
)
from starplot.styles import MarkerSymbolEnum


class DsoPlotterMixin:
    def _plot_dso_polygon(self, polygon, style):
        coords = list(zip(*polygon.exterior.coords.xy))
        # close the polygon - for some reason matplotlib needs the coord twice
        coords.append(coords[0])
        coords.append(coords[0])
        self._polygon(coords, style.marker.to_polygon_style(), closed=False)

    def open_clusters(self, *args, **kwargs):
        self.dsos(types=[DsoType.OPEN_CLUSTER], **kwargs)

    def globular_clusters(self, *args, **kwargs):
        self.dsos(types=[DsoType.GLOBULAR_CLUSTER], **kwargs)

    def galaxies(self, *args, **kwargs):
        """
        Plots galaxy DSO types

        This is just a small wrapper around the `dsos()` function, so any `kwargs` will be passed through.
        """
        self.dsos(
            types=[
                DsoType.GALAXY,
                DsoType.GALAXY_PAIR,
                DsoType.GALAXY_TRIPLET,
            ],
            **kwargs,
        )

    def nebula(self, *args, **kwargs):
        """Plots nebula DSO types

        This is just a small wrapper around the `dsos()` function, so any `kwargs` will be passed through.
        """
        self.dsos(
            types=[
                DsoType.NEBULA,
                DsoType.PLANETARY_NEBULA,
                DsoType.EMISSION_NEBULA,
                DsoType.STAR_CLUSTER_NEBULA,
                DsoType.REFLECTION_NEBULA,
            ],
            **kwargs,
        )

    def dsos(
        self,
        mag: float = 8.0,
        types: list[DsoType] = DEFAULT_DSO_TYPES,
        names: list[str] = None,
        null: bool = False,
        true_size: bool = True,
        labels: Mapping[str, str] = DSO_LABELS_DEFAULT,
        legend_labels: Mapping[DsoType, str] = DSO_LEGEND_LABELS,
    ):
        """
        Plots Deep Sky Objects (DSOs), from OpenNGC

        Args:
            mag: Limiting magnitude of DSOs to plot
            types: List of DSO types to plot
            names: List of DSO names (as specified in OpenNGC) to filter by (case sensitive!). If `None`, then the DSOs will not be filtered by name.
            null: If True, then DSOs without a defined magnitude will be plotted
            true_size: If True, then each DSO will be plotted as its true apparent size in the sky (note: this increases plotting time). If False, then the style's marker size will be used. Also, keep in mind not all DSOs have a defined size (according to OpenNGC) -- so these will use the style's marker size.
            labels: A dictionary that maps DSO names (as specified in OpenNGC) to the label that'll be plotted for that object. By default, the DSO's name in OpenNGC will be used as the label. If you want to hide all labels, then set this arg to `None`.
            legend_labels: A dictionary that maps a `DsoType` to the legend label that'll be plotted for that type of DSO. If you want to hide all DSO legend labels, then set this arg to `None`.

        """

        # TODO: add args mag_labels, styles

        # TODO: sort by type, and plot markers together (for better performance)

        self.logger.debug("Plotting DSOs...")
        ongc = gpd.read_file(
            DataFiles.ONGC.value,
            engine="pyogrio",
            use_arrow=True,
            bbox=self._extent_mask(),
        )

        if labels is None:
            labels = {}
        elif type(labels) != DsoLabelMaker:
            labels = DsoLabelMaker(overrides=labels)

        if legend_labels is None:
            legend_labels = {}
        else:
            legend_labels = {**DSO_LEGEND_LABELS, **legend_labels}

        dso_types = [ONGC_TYPE[dtype] for dtype in types]
        nearby_dsos = ongc[ongc["Type"].isin(dso_types)]
        nearby_dsos = nearby_dsos.replace({np.nan: None})

        if names:
            nearby_dsos = nearby_dsos[nearby_dsos["Name"].isin(names)]

        for n, d in nearby_dsos.iterrows():
            if d.ra_degrees is None or d.dec_degrees is None:
                continue

            ra = d.ra_degrees
            dec = d.dec_degrees

            name = d.Name
            label = labels.get(name)
            dso_type = ONGC_TYPE_MAP[d.Type]
            style = self.style.get_dso_style(dso_type)
            maj_ax, min_ax, angle = d.MajAx, d.MinAx, d.PosAng
            legend_label = legend_labels.get(dso_type)
            magnitude = d["V-Mag"] or d["B-Mag"] or None
            magnitude = float(magnitude) if magnitude else None

            if (
                not style
                or (magnitude is not None and magnitude > mag)
                or (magnitude is None and not null)
            ):
                continue

            geometry_types = d["geometry"].geom_type

            if true_size:
                if "Polygon" in geometry_types and "MultiPolygon" not in geometry_types:
                    self._plot_dso_polygon(d.geometry, style)

                elif "MultiPolygon" in geometry_types:
                    for polygon in d.geometry.geoms:
                        self._plot_dso_polygon(polygon, style)
                elif maj_ax:
                    # if object has a major axis then plot its actual extent

                    maj_ax_degrees = (maj_ax / 60) / 2

                    if min_ax:
                        min_ax_degrees = (min_ax / 60) / 2
                    else:
                        min_ax_degrees = maj_ax_degrees

                    poly_style = style.marker.to_polygon_style()

                    if style.marker.symbol == MarkerSymbolEnum.SQUARE:
                        self.rectangle(
                            (ra / 15, dec),
                            min_ax_degrees * 2,
                            maj_ax_degrees * 2,
                            poly_style,
                            angle or 0,
                        )
                    else:
                        self.ellipse(
                            (ra / 15, dec),
                            min_ax_degrees * 2,
                            maj_ax_degrees * 2,
                            poly_style,
                            angle or 0,
                        )

                if label:
                    self._plot_text(
                        ra / 15,
                        dec,
                        label,
                        **style.label.matplot_kwargs(self._size_multiplier),
                    )

            else:
                # if no major axis, then just plot as a marker
                self.marker(
                    ra=ra / 15,
                    dec=dec,
                    label=label,
                    style=style,
                )

            self._add_legend_handle_marker(legend_label, style.marker)
