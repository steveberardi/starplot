from starplot import geometry
from starplot.coordinates import CoordinateSystem
from starplot.data.translations import translate
from starplot.plots.map import MapPlot
from starplot.models.observer import Observer
from starplot.projections import Stereographic, Equidistant
from starplot.styles import (
    LabelStyle,
    PlotStyle,
    PathStyle,
    GradientDirection,
    extensions,
)
from starplot.styles.helpers import use_style
from starplot.plotters.text import CollisionHandler
from starplot.profile import profile


class ZenithPlot(MapPlot):
    """Creates a new zenith plot.

    Args:
        observer: Observer instance which specifies a time and place. Defaults to `Observer()`
        ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        style: Styling for the plot (colors, sizes, fonts, etc). If `None`, it defaults to `PlotStyle()`
        resolution: Size (in pixels) of largest dimension of the map
        point_label_handler: Default [CollisionHandler][starplot.CollisionHandler] for point labels.
        area_label_handler: Default [CollisionHandler][starplot.CollisionHandler] for area labels.
        path_label_handler: Default [CollisionHandler][starplot.CollisionHandler] for path labels.
        scale: Scaling factor that will be applied to all sizes in styles (e.g. font size, marker size, line widths, etc). For example, if you want to make everything 2x bigger, then set the scale to 2. At `scale=1` and `resolution=4096` (the default), all sizes are optimized visually for a map that covers 1-3 constellations. So, if you're creating a plot of a _larger_ extent, then it'd probably be good to decrease the scale (i.e. make everything smaller) -- and _increase_ the scale if you're plotting a very small area.
        autoscale: If True, then the scale will be set automatically based on resolution.
        suppress_warnings: If True (the default), then all warnings will be suppressed

    Returns:
        ZenithPlot: A new instance of a ZenithPlot

    """

    _coordinate_system = CoordinateSystem.RA_DEC

    def __init__(
        self,
        observer: Observer = None,
        ephemeris: str = "de421.bsp",
        style: PlotStyle = None,
        resolution: int = 4096,
        point_label_handler: CollisionHandler = None,
        area_label_handler: CollisionHandler = None,
        path_label_handler: CollisionHandler = None,
        scale: float = 1.0,
        autoscale: bool = False,
        suppress_warnings: bool = True,
        *args,
        **kwargs,
    ) -> "ZenithPlot":
        observer = observer or Observer()
        style = style or PlotStyle().extend(extensions.MAP)

        projection = Stereographic(
            center_ra=observer.lst,
            center_dec=observer.lat,
        )

        clip_path = geometry.circle(
            center=(observer.lst, observer.lat),
            diameter_degrees=180,
            num_pts=400,
        )

        super().__init__(
            projection,
            0,
            360,
            -90,
            90,
            observer=observer,
            ephemeris=ephemeris,
            style=style,
            resolution=resolution,
            point_label_handler=point_label_handler,
            area_label_handler=area_label_handler,
            path_label_handler=path_label_handler,
            clip_path=clip_path,
            scale=scale,
            autoscale=autoscale,
            suppress_warnings=suppress_warnings,
            *args,
            **kwargs,
        )

    @profile
    @use_style(PathStyle, "horizon")
    def horizon(
        self,
        style: PathStyle = None,
        labels: list = ["N", "E", "S", "W"],
    ):
        """
        Plots the horizon for the observer of the plot

        Args:
            style: Style of the horizon path. If None, then the plot's style definition will be used.
            labels: List of labels for cardinal directions. **NOTE: labels should be in the order: North, East, South, West.**
        """
        if self.observer is None:
            raise ValueError("observer is required for plotting the horizon")

        _labels = []
        if labels:
            _labels = [
                (
                    [self.observer.radec(0, alt) for alt in range(-5, 6, 5)],
                    labels[0],
                    ("top",),
                ),
                (
                    [self.observer.radec(90, alt) for alt in range(-5, 6, 5)],
                    labels[1],
                    ("left",),
                ),
                (
                    [self.observer.radec(180, alt) for alt in range(-5, 6, 5)],
                    labels[2],
                    ("bottom",),
                ),
                (
                    [self.observer.radec(270, alt) for alt in range(-5, 6, 5)],
                    labels[3],
                    ("right",),
                ),
            ]

        self.canvas._clip_path_border(style, labels=_labels)

    def _adjust_radec_minmax(self):
        self.ra_min = 0
        self.ra_max = 360
        self.dec_min = -90
        self.dec_max = 90

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
