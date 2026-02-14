import numpy as np
from matplotlib import path, patches

from starplot.coordinates import CoordinateSystem
from starplot.data.translations import translate
from starplot.plots.map import MapPlot
from starplot.models.observer import Observer
from starplot.projections import Stereographic
from starplot.styles import (
    LabelStyle,
    PlotStyle,
    PathStyle,
    GradientDirection,
    extensions,
)
from starplot.styles.helpers import use_style
from starplot.plotters.text import CollisionHandler


class ZenithPlot(MapPlot):
    """Creates a new zenith plot.

    Args:
        observer: Observer instance which specifies a time and place. Defaults to `Observer()`
        ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        style: Styling for the plot (colors, sizes, fonts, etc). If `None`, it defaults to `PlotStyle()`
        resolution: Size (in pixels) of largest dimension of the map
        collision_handler: Default [CollisionHandler][starplot.CollisionHandler] for the plot that describes what to do on label collisions with other labels, markers, etc.
        scale: Scaling factor that will be applied to all sizes in styles (e.g. font size, marker size, line widths, etc). For example, if you want to make everything 2x bigger, then set the scale to 2. At `scale=1` and `resolution=4096` (the default), all sizes are optimized visually for a map that covers 1-3 constellations. So, if you're creating a plot of a _larger_ extent, then it'd probably be good to decrease the scale (i.e. make everything smaller) -- and _increase_ the scale if you're plotting a very small area.
        autoscale: If True, then the scale will be set automatically based on resolution.
        suppress_warnings: If True (the default), then all warnings will be suppressed

    Returns:
        ZenithPlot: A new instance of a ZenithPlot

    """

    _coordinate_system = CoordinateSystem.RA_DEC
    _gradient_direction = GradientDirection.RADIAL

    def __init__(
        self,
        observer: Observer = None,
        ephemeris: str = "de421.bsp",
        style: PlotStyle = None,
        resolution: int = 4096,
        collision_handler: CollisionHandler = None,
        scale: float = 1.0,
        autoscale: bool = False,
        suppress_warnings: bool = True,
        *args,
        **kwargs,
    ) -> "ZenithPlot":
        observer = observer or Observer()
        projection = Stereographic(
            center_ra=observer.lst,
            center_dec=observer.lat,
        )
        style = style or PlotStyle().extend(extensions.MAP)

        super().__init__(
            projection,
            0,
            360,
            -90,
            90,
            observer,
            ephemeris,
            style,
            resolution,
            collision_handler=collision_handler,
            clip_path=None,
            scale=scale,
            autoscale=autoscale,
            suppress_warnings=suppress_warnings,
            *args,
            **kwargs,
        )

    @use_style(PathStyle, "horizon")
    def horizon(
        self,
        style: PathStyle = None,
        labels: list = ["N", "E", "S", "W"],
    ):
        """
        Draws a [great circle](https://en.wikipedia.org/wiki/Great_circle) representing the horizon for the given `lat`, `lon` at time `dt` (so you must define these when creating the plot to use this function)

        Args:
            style: Style of the horizon path. If None, then the plot's style definition will be used.
            labels: List of labels for cardinal directions. **NOTE: labels should be in the order: North, East, South, West.**
        """
        if self.observer is None:
            raise ValueError("observer is required for plotting the horizon")

        """
        For zenith projections, we plot the horizon as a patch to make a more perfect circle
        """
        style_kwargs = style.line.matplot_kwargs(self.scale)
        style_kwargs["clip_on"] = False
        style_kwargs["edgecolor"] = style_kwargs.pop("color")
        patch = patches.Circle(
            (0.50, 0.50),
            radius=0.454,
            facecolor=None,
            fill=False,
            transform=self.ax.transAxes,
            **style_kwargs,
        )
        self.ax.add_patch(patch)
        self._background_clip_path = patch
        self._update_clip_path_polygon(
            buffer=style.line.width / 2 + 2 * style.line.edge_width + 40
        )

        if not labels:
            return

        labels = [translate(label, self.language) for label in labels]

        label_ax_coords = [
            (0.5, 0.95),  # north
            (0.045, 0.5),  # east
            (0.5, 0.045),  # south
            (0.954, 0.5),  # west
        ]
        for label, coords in zip(labels, label_ax_coords):
            self.ax.annotate(
                label,
                coords,
                xycoords=self.ax.transAxes,
                clip_on=False,
                **style.label.matplot_kwargs(self.scale),
            )

    def _adjust_radec_minmax(self):
        self.ra_min = 0
        self.ra_max = 360
        self.dec_min = -90
        self.dec_max = 90

    def _set_extent(self):
        theta = np.linspace(0, 2 * np.pi, 100)
        center, radius = [0.5, 0.5], 0.45
        verts = np.vstack([np.sin(theta), np.cos(theta)]).T
        circle = path.Path(verts * radius + center)
        extent = self.ax.get_extent(crs=self._proj)
        self.ax.set_extent((p / 3.548 for p in extent), crs=self._proj)
        self.ax.set_boundary(circle, transform=self.ax.transAxes)

    @use_style(LabelStyle, "info_text")
    def info(self, style: LabelStyle = None):
        """
        Plots info text in the lower left corner, including date/time and lat/lon.

        Args:
            style: Styling of the info text. If None, then the plot's style definition will be used.
        """
        dt_str = self.dt.strftime("%m/%d/%Y @ %H:%M:%S") + " " + self.dt.tzname()
        info = f"{str(self.observer.lat)}, {str(self.observer.lon)}\n{dt_str}"
        self.ax.text(
            0.05,
            0.05,
            info,
            transform=self.ax.transAxes,
            **style.matplot_kwargs(self.scale),
        )

    def _plot_background_clip_path(self):
        if self.style.has_gradient_background():
            background_color = "#ffffff00"
            self._plot_gradient_background(self.style.background_color)
        else:
            background_color = self.style.background_color.as_hex()

        self._background_clip_path = patches.Circle(
            (0.50, 0.50),
            radius=0.45,
            fill=True,
            facecolor=background_color,
            # edgecolor=self.style.border_line_color.as_hex(),
            linewidth=0,
            zorder=-2_000,
            transform=self.ax.transAxes,
        )
        self.ax.set_facecolor(background_color)

        self.ax.add_patch(self._background_clip_path)
        self._update_clip_path_polygon(buffer=20)

    def _prepare_star_coords(self, df, limit_by_altaz=False):
        # TODO : reconcile this commented code
        # self.location = self.earth + wgs84.latlon(
        #     self.observer.lat, self.observer.lon
        # )
        # df["ra_hours"], df["dec_degrees"] = (df.ra / 15, df.dec)
        # stars_apparent = (
        #     self.location.at(self.observer.timescale)
        #     .observe(SkyfieldStar.from_dataframe(df))
        #     .apparent()
        # )
        # # we only need altitude
        # stars_alt, _, _ = stars_apparent.altaz()
        # df["alt"] = stars_alt.degrees
        # df = df[df["alt"] > 0]

        df["x"], df["y"] = (
            df["ra"],
            df["dec"],
        )
        return df
