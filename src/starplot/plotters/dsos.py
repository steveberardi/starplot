from typing import Callable, Mapping

from ibis import _
import numpy as np

from starplot.data.dsos import (
    DSO_LABELS_DEFAULT,
    DsoLabelMaker,
    load,
)
from starplot.models.dso import (
    DSO,
    DsoType,
    from_tuple,
    ONGC_TYPE_MAP,
    DSO_LEGEND_LABELS,
)
from starplot.styles import MarkerSymbolEnum
from starplot.profile import profile


class DsoPlotterMixin:
    def _plot_dso_polygon(self, polygon, style):
        coords = list(zip(*polygon.exterior.coords.xy))
        # close the polygon - for some reason matplotlib needs the coord twice
        coords.append(coords[0])
        coords.append(coords[0])
        self._polygon(coords, style.marker.to_polygon_style(), closed=False)

    def messier(self, **kwargs):
        """
        Plots Messier objects

        This is just a small wrapper around the `dsos()` function, so any `kwargs` will be passed through.
        """
        where = kwargs.pop("where", [])
        where.append(_.m.notnull())
        self.dsos(where=where, **kwargs)

    def open_clusters(self, **kwargs):
        """
        Plots open clusters

        This is just a small wrapper around the `dsos()` function, so any `kwargs` will be passed through.
        """
        where = kwargs.pop("where", [])
        where.append(_.type == DsoType.OPEN_CLUSTER.value)
        self.dsos(where=where, **kwargs)

    def globular_clusters(self, **kwargs):
        """
        Plots globular clusters

        This is just a small wrapper around the `dsos()` function, so any `kwargs` will be passed through.
        """
        where = kwargs.pop("where", [])
        where.append(_.type == DsoType.GLOBULAR_CLUSTER.value)
        self.dsos(where=where, **kwargs)

    def galaxies(self, **kwargs):
        """
        Plots galaxy DSO types:

        - Galaxy
        - Galaxy Pair
        - Galaxy Triplet

        This is just a small wrapper around the `dsos()` function, so any `kwargs` will be passed through.
        """
        galaxy_types = [
            DsoType.GALAXY.value,
            DsoType.GALAXY_PAIR.value,
            DsoType.GALAXY_TRIPLET.value,
        ]
        where = kwargs.pop("where", [])
        where.append(_.type.isin(galaxy_types))
        self.dsos(where=where, **kwargs)

    def nebula(self, **kwargs):
        """
        Plots nebula DSO types:

        - Nebula
        - Planetary Nebula
        - Emission Nebula
        - Star Cluster Nebula
        - Reflection Nebula
        - HII Ionized Regions

        * Note that this does NOT plot dark nebulae

        This is just a small wrapper around the `dsos()` function, so any `kwargs` will be passed through.
        """
        nebula_types = [
            DsoType.NEBULA.value,
            DsoType.PLANETARY_NEBULA.value,
            DsoType.EMISSION_NEBULA.value,
            DsoType.STAR_CLUSTER_NEBULA.value,
            DsoType.REFLECTION_NEBULA.value,
            DsoType.HII_IONIZED_REGION.value,
        ]
        where = kwargs.pop("where", [])
        where.append(_.type.isin(nebula_types))
        self.dsos(where=where, **kwargs)

    @profile
    def dsos(
        self,
        where: list = None,
        where_labels: list = None,
        true_size: bool = True,
        labels: Mapping[str, str] = DSO_LABELS_DEFAULT,
        legend_labels: Mapping[DsoType, str] = DSO_LEGEND_LABELS,
        alpha_fn: Callable[[DSO], float] = None,
        label_fn: Callable[[DSO], str] = None,
        sql: str = None,
        sql_labels: str = None,
    ):
        """
        Plots Deep Sky Objects (DSOs), from OpenNGC

        Args:
            where: A list of expressions that determine which DSOs to plot. See [Selecting Objects](/reference-selecting-objects/) for details.
            where_labels: A list of expressions that determine which DSOs are labeled on the plot. See [Selecting Objects](/reference-selecting-objects/) for details.
            true_size: If True, then each DSO will be plotted as its true apparent size in the sky (note: this increases plotting time). If False, then the style's marker size will be used. Also, keep in mind not all DSOs have a defined size (according to OpenNGC) -- so these will use the style's marker size.
            labels: A dictionary that maps DSO names (as specified in OpenNGC) to the label that'll be plotted for that object. By default, the DSO's name in OpenNGC will be used as the label. If you want to hide all labels, then set this arg to `None`.
            legend_labels: A dictionary that maps a `DsoType` to the legend label that'll be plotted for that type of DSO. If you want to hide all DSO legend labels, then set this arg to `None`.
            alpha_fn: Callable for calculating the alpha value (aka "opacity") of each DSO. If `None`, then the marker style's alpha will be used.
            label_fn: Callable for determining the label of each DSO. If `None`, then the names in the `labels` kwarg will be used.
            sql: SQL query for selecting DSOs (table name is `_`). This query will be applied _after_ any filters in the `where` kwarg.
            sql_labels: SQL query for selecting DSOs that will be labeled (table name is `_`). Applied _after_ any filters in the `where_labels` kwarg.
        """

        # TODO: add kwarg styles

        where = where or []
        where_labels = where_labels or []

        if labels is None:
            labels = {}
        elif type(labels) != DsoLabelMaker:
            labels = DsoLabelMaker(overrides=labels)

        if legend_labels is None:
            legend_labels = {}
        else:
            legend_labels = {**DSO_LEGEND_LABELS, **legend_labels}

        extent = self._extent_mask()
        dso_results = load(extent=extent, filters=where, sql=sql)

        dso_results_labeled = dso_results
        for f in where_labels:
            dso_results_labeled = dso_results_labeled.filter(f)

        if sql_labels:
            result = (
                dso_results_labeled.alias("_").sql(sql_labels).select("sk").execute()
            )
            skids = result["sk"].to_list()
            dso_results_labeled = dso_results_labeled.filter(_.sk.isin(skids))

        label_row_ids = dso_results_labeled.to_pandas()["rowid"].tolist()

        results_df = dso_results.to_pandas()
        results_df = results_df.replace({np.nan: None})

        for d in results_df.itertuples():
            ra = d.ra_degrees
            dec = d.dec_degrees
            dso_type = ONGC_TYPE_MAP[d.type]
            style = self.style.get_dso_style(dso_type)
            maj_ax, min_ax, angle = d.maj_ax, d.min_ax, d.angle
            legend_label = legend_labels.get(dso_type)
            _dso = from_tuple(d)
            label = labels.get(d.name) if label_fn is None else label_fn(_dso)

            if style is None:
                continue

            _alpha_fn = alpha_fn or (lambda d: style.marker.alpha)
            style.marker.alpha = _alpha_fn(_dso)

            if _dso._row_id not in label_row_ids:
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
                            (ra, dec),
                            min_ax_degrees * 2,
                            maj_ax_degrees * 2,
                            style=poly_style,
                            angle=angle or 0,
                        )
                    else:
                        self.ellipse(
                            (ra, dec),
                            min_ax_degrees * 2,
                            maj_ax_degrees * 2,
                            style=poly_style,
                            angle=angle or 0,
                        )

                if label:
                    self.text(label, ra, dec, style.label, gid=f"dso-{d.type}-label")

            else:
                # if no major axis, then just plot as a marker
                self.marker(
                    ra=ra,
                    dec=dec,
                    style=style,
                    label=label,
                    skip_bounds_check=True,
                    gid_marker=f"dso-{d.type}-marker",
                    gid_label=f"dso-{d.type}-label",
                )

            self._objects.dsos.append(_dso)

            self._add_legend_handle_marker(legend_label, style.marker)
