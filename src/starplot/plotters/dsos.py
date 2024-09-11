from functools import cache
from typing import Callable, Mapping

from starplot.data.dsos import (
    DsoType,
    ONGC_TYPE_MAP,
    DSO_LEGEND_LABELS,
    DSO_LABELS_DEFAULT,
    DsoLabelMaker,
    load_ongc,
)
from starplot.models.dso import DSO, from_tuple
from starplot.styles import MarkerSymbolEnum


def _where(*args, **kwargs):
    where = kwargs.pop("where", [])

    if mag := kwargs.pop("mag", None):
        where.append(DSO.magnitude.is_null() | (DSO.magnitude <= mag))
    return where


class DsoPlotterMixin:
    def _plot_dso_polygon(self, polygon, style):
        coords = list(zip(*polygon.exterior.coords.xy))
        # close the polygon - for some reason matplotlib needs the coord twice
        coords.append(coords[0])
        coords.append(coords[0])
        self._polygon(coords, style.marker.to_polygon_style(), closed=False)

    def messier(self, *args, **kwargs):
        """
        Plots Messier objects

        This is just a small wrapper around the `dsos()` function, so any `kwargs` will be passed through.
        """
        where = _where(**kwargs)
        where.append(DSO.m.is_not_null())
        kwargs.pop("where", None)
        self.dsos(where=where, **kwargs)

    def open_clusters(self, *args, **kwargs):
        """
        Plots open clusters

        This is just a small wrapper around the `dsos()` function, so any `kwargs` will be passed through.
        """
        where = _where(**kwargs)
        where.append(DSO.type == DsoType.OPEN_CLUSTER)
        kwargs.pop("where", None)
        self.dsos(where=where, **kwargs)

    def globular_clusters(self, *args, **kwargs):
        """
        Plots globular clusters

        This is just a small wrapper around the `dsos()` function, so any `kwargs` will be passed through.
        """
        where = _where(**kwargs)
        where.append(DSO.type == DsoType.GLOBULAR_CLUSTER)
        kwargs.pop("where", None)
        self.dsos(where=where, **kwargs)

    def galaxies(self, *args, **kwargs):
        """
        Plots galaxy DSO types:

        - Galaxy
        - Galaxy Pair
        - Galaxy Triplet

        This is just a small wrapper around the `dsos()` function, so any `kwargs` will be passed through.
        """
        galaxy_types = [
            DsoType.GALAXY,
            DsoType.GALAXY_PAIR,
            DsoType.GALAXY_TRIPLET,
        ]
        where = _where(**kwargs)
        where.append(DSO.type.is_in(galaxy_types))
        kwargs.pop("where", None)
        self.dsos(where=where, **kwargs)

    def nebula(self, *args, **kwargs):
        """
        Plots nebula DSO types:

        - Nebula
        - Planetary Nebula
        - Emission Nebula
        - Star Cluster Nebula
        - Reflection Nebula

        This is just a small wrapper around the `dsos()` function, so any `kwargs` will be passed through.
        """
        nebula_types = [
            DsoType.NEBULA,
            DsoType.PLANETARY_NEBULA,
            DsoType.EMISSION_NEBULA,
            DsoType.STAR_CLUSTER_NEBULA,
            DsoType.REFLECTION_NEBULA,
        ]
        where = _where(**kwargs)
        where.append(DSO.type.is_in(nebula_types))
        kwargs.pop("where", None)
        self.dsos(where=where, **kwargs)

    @cache
    def _load_dsos(self):
        return load_ongc(bbox=self._extent_mask())

    def dsos(
        self,
        mag: float = 8.0,
        true_size: bool = True,
        labels: Mapping[str, str] = DSO_LABELS_DEFAULT,
        legend_labels: Mapping[DsoType, str] = DSO_LEGEND_LABELS,
        alpha_fn: Callable[[DSO], float] = None,
        label_fn: Callable[[DSO], str] = None,
        where: list = None,
        where_labels: list = None,
    ):
        """
        Plots Deep Sky Objects (DSOs), from OpenNGC

        Args:
            mag: Limiting magnitude of DSOs to plot. For more control of what DSOs to plot, use the `where` kwarg. **Note:** if you pass `mag` and `where` then `mag` will be ignored
            true_size: If True, then each DSO will be plotted as its true apparent size in the sky (note: this increases plotting time). If False, then the style's marker size will be used. Also, keep in mind not all DSOs have a defined size (according to OpenNGC) -- so these will use the style's marker size.
            labels: A dictionary that maps DSO names (as specified in OpenNGC) to the label that'll be plotted for that object. By default, the DSO's name in OpenNGC will be used as the label. If you want to hide all labels, then set this arg to `None`.
            legend_labels: A dictionary that maps a `DsoType` to the legend label that'll be plotted for that type of DSO. If you want to hide all DSO legend labels, then set this arg to `None`.
            alpha_fn: Callable for calculating the alpha value (aka "opacity") of each DSO. If `None`, then the marker style's alpha will be used.
            label_fn: Callable for determining the label of each DSO. If `None`, then the names in the `labels` kwarg will be used.
            where: A list of expressions that determine which DSOs to plot. See [Selecting Objects](/reference-selecting-objects/) for details.
            where_labels: A list of expressions that determine which DSOs are labeled on the plot. See [Selecting Objects](/reference-selecting-objects/) for details.
        """

        # TODO: add kwarg styles

        self.logger.debug("Plotting DSOs...")

        where = where or []
        where_labels = where_labels or []

        if not where:
            where = [DSO.magnitude.is_null() | (DSO.magnitude <= mag)]

        if labels is None:
            labels = {}
        elif type(labels) != DsoLabelMaker:
            labels = DsoLabelMaker(overrides=labels)

        if legend_labels is None:
            legend_labels = {}
        else:
            legend_labels = {**DSO_LEGEND_LABELS, **legend_labels}

        nearby_dsos = self._load_dsos()  # load_ongc(bbox=self._extent_mask())
        # dso_types = [ONGC_TYPE[dtype] for dtype in types]
        # nearby_dsos = nearby_dsos[nearby_dsos["type"].isin(dso_types)]

        for d in nearby_dsos.itertuples():
            ra = d.ra_degrees
            dec = d.dec_degrees
            dso_type = ONGC_TYPE_MAP[d.type]
            style = self.style.get_dso_style(dso_type)
            maj_ax, min_ax, angle = d.maj_ax, d.min_ax, d.angle
            legend_label = legend_labels.get(dso_type)
            magnitude = d.mag_v or d.mag_b or None
            magnitude = float(magnitude) if magnitude else None
            _dso = from_tuple(d)
            label = labels.get(d.name) if label_fn is None else label_fn(_dso)

            if any(
                [
                    style is None,
                    not all([e.evaluate(_dso) for e in where]),
                    # not self.in_bounds(ra / 15, dec),
                ]
            ):
                continue

            _alpha_fn = alpha_fn or (lambda d: style.marker.alpha)
            style.marker.alpha = _alpha_fn(_dso)

            if where_labels and not all([e.evaluate(_dso) for e in where_labels]):
                label = None

            if true_size and d.size_deg2 is not None:
                if "Polygon" == str(d.geometry.geom_type):
                    self._plot_dso_polygon(d.geometry, style)

                elif "MultiPolygon" == str(d.geometry.geom_type):
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
                            style=poly_style,
                            angle=angle or 0,
                        )
                    else:
                        self.ellipse(
                            (ra / 15, dec),
                            min_ax_degrees * 2,
                            maj_ax_degrees * 2,
                            style=poly_style,
                            angle=angle or 0,
                        )

                if label:
                    self.text(label, ra / 15, dec, style.label)

            else:
                # if no major axis, then just plot as a marker
                self.marker(
                    ra=ra / 15,
                    dec=dec,
                    label=label,
                    style=style,
                    skip_bounds_check=True,
                )

            self._objects.dsos.append(_dso)

            self._add_legend_handle_marker(legend_label, style.marker)
