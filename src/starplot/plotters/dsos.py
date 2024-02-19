import geopandas as gpd
import numpy as np

from starplot.data import DataFiles, dsos
from starplot.models import SkyObject
from starplot.styles import PlotStyle, PolygonStyle, MarkerSymbolEnum


class DsoPlotterMixin:
    def _plot_dso_polygon(self, polygon, style):
        coords = list(zip(*polygon.exterior.coords.xy))
        # close the polygon - for some reason matplotlib needs the coord twice
        coords.append(coords[0])
        coords.append(coords[0])
        self._plot_polygon(coords, style.marker.to_polygon_style(), closed=False)

        # coords = [(ra * -1, dec) for ra, dec in coords]
        # p = Polygon(coords)
        # poly_style = style.marker.to_polygon_style()
        # pstyle = poly_style.matplot_kwargs(size_multiplier=self._size_multiplier)
        # pstyle.pop("fill", None)
        # self.ax.add_geometries([polygon], crs=self._plate_carree, **pstyle)

    def plot_dsos(self, limiting_magnitude: float = 8.0, types: list[dsos.DsoType] = dsos.DEFAULT_DSO_TYPES, plot_null_magnitudes: bool = False):
        """
        Plots Deep Sky Objects (DSOs), from OpenNGC
        
        Args:
            limiting_magnitude: Limiting magnitude of DSOs to plot
            types: List of DSO types to plot
            plot_null_magnitudes: If True, then DSOs without a defined magnitude will be plotted
        
        """
        ongc = gpd.read_file(
            DataFiles.ONGC.value,
            engine="pyogrio",
            use_arrow=True,
            bbox=self._extent_mask(),
        )

        dso_types = [dsos.ONGC_TYPE[dtype] for dtype in types]
        nearby_dsos = ongc[ongc["Type"].isin(dso_types)]
        nearby_dsos = nearby_dsos.replace({np.nan: None})

        for n, d in nearby_dsos.iterrows():
            if d.ra_degrees is None or d.dec_degrees is None:
                continue

            ra = d.ra_degrees
            dec = d.dec_degrees

            name = d.Name
            dso_type = dsos.ONGC_TYPE_MAP[d.Type]
            style = self.style.get_dso_style(dso_type)
            maj_ax, min_ax, angle = d.MajAx, d.MinAx, d.PosAng
            legend_label = dsos.LEGEND_LABELS.get(dso_type) or dso_type
            magnitude = d["V-Mag"] or d["B-Mag"] or None
            magnitude = float(magnitude) if magnitude else None

            if (
                not style
                or not style.marker.visible
                or (magnitude is not None and magnitude > limiting_magnitude)
                or (magnitude is None and not plot_null_magnitudes)
            ):
                continue

            geometry_types = d["geometry"].geom_type

            if "Polygon" in geometry_types and "MultiPolygon" not in geometry_types:
                self._plot_dso_polygon(d.geometry, style)

            elif "MultiPolygon" in geometry_types:
                for polygon in d.geometry.geoms:
                    self._plot_dso_polygon(polygon, style)
            elif maj_ax:
                # If object has a major axis then plot it's actual extent

                maj_ax_degrees = (maj_ax / 60) / 2

                if min_ax:
                    min_ax_degrees = (min_ax / 60) / 2
                else:
                    min_ax_degrees = maj_ax_degrees

                poly_style = style.marker.to_polygon_style()

                if style.marker.symbol == MarkerSymbolEnum.SQUARE:
                    self.plot_rectangle(
                        (ra / 15, dec),
                        min_ax_degrees * 2,
                        maj_ax_degrees * 2,
                        poly_style,
                        angle or 0,
                    )
                else:
                    self.plot_ellipse(
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