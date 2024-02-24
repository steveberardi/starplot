import geopandas as gpd
import numpy as np

from starplot.data import DataFiles
from starplot.data.dsos import (
    DsoType,
    DEFAULT_DSO_TYPES,
    ONGC_TYPE,
    ONGC_TYPE_MAP,
    LEGEND_LABELS,
)
from starplot.models import SkyObject
from starplot.styles import MarkerSymbolEnum


class DsoPlotterMixin:
    def _plot_dso_polygon(self, polygon, style):
        coords = list(zip(*polygon.exterior.coords.xy))
        # close the polygon - for some reason matplotlib needs the coord twice
        coords.append(coords[0])
        coords.append(coords[0])
        self._polygon(coords, style.marker.to_polygon_style(), closed=False)

        # coords = [(ra * -1, dec) for ra, dec in coords]
        # p = Polygon(coords)
        # poly_style = style.marker.to_polygon_style()
        # pstyle = poly_style.matplot_kwargs(size_multiplier=self._size_multiplier)
        # pstyle.pop("fill", None)
        # self.ax.add_geometries([polygon], crs=self._plate_carree, **pstyle)

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
        null: bool = False,
        true_size: bool = True,
    ):
        """
        Plots Deep Sky Objects (DSOs), from OpenNGC

        Args:
            mag: Limiting magnitude of DSOs to plot
            types: List of DSO types to plot
            null: If True, then DSOs without a defined magnitude will be plotted
            true_size: If True, then each DSO will be plotted as its true apparent size in the sky (note: this increases plotting time). If False, then the style's marker size will be used. Also, keep in mind not all DSOs have a defined size (according to OpenNGC) -- so these will use the style's marker size.

        """
        ongc = gpd.read_file(
            DataFiles.ONGC.value,
            engine="pyogrio",
            use_arrow=True,
            bbox=self._extent_mask(),
        )

        dso_types = [ONGC_TYPE[dtype] for dtype in types]
        nearby_dsos = ongc[ongc["Type"].isin(dso_types)]
        nearby_dsos = nearby_dsos.replace({np.nan: None})

        # TODO: sort by type, and plot markers together

        for n, d in nearby_dsos.iterrows():
            if d.ra_degrees is None or d.dec_degrees is None:
                continue

            ra = d.ra_degrees
            dec = d.dec_degrees

            name = d.Name
            dso_type = ONGC_TYPE_MAP[d.Type]
            style = self.style.get_dso_style(dso_type)
            maj_ax, min_ax, angle = d.MajAx, d.MinAx, d.PosAng
            legend_label = LEGEND_LABELS.get(dso_type) or dso_type
            magnitude = d["V-Mag"] or d["B-Mag"] or None
            magnitude = float(magnitude) if magnitude else None

            if (
                not style
                or not style.marker.visible
                or (magnitude is not None and magnitude > mag)
                or (magnitude is None and not null)
            ):
                continue

            geometry_types = d["geometry"].geom_type

            if (
                true_size
                and "Polygon" in geometry_types
                and "MultiPolygon" not in geometry_types
            ):
                self._plot_dso_polygon(d.geometry, style)

            elif true_size and "MultiPolygon" in geometry_types:
                for polygon in d.geometry.geoms:
                    self._plot_dso_polygon(polygon, style)
            elif true_size and maj_ax:
                # If object has a major axis then plot it's actual extent

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

                if style.label.visible:
                    self._plot_text(
                        ra,
                        dec,
                        d.name,
                        **style.label.matplot_kwargs(self._size_multiplier),
                    )

            else:
                # If no major axis, then just plot as a marker
                obj = SkyObject(
                    name=name,
                    ra=ra / 15,
                    dec=dec,
                    style=style,
                )
                self.plot_object(obj)

            self._add_legend_handle_marker(legend_label, style.marker)
