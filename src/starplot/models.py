from pydantic import BaseModel

from starplot.styles import ObjectStyle


class SkyObject(BaseModel):
    """
    Model for plotting additional objects (e.g. DSOs)

    Example Usage:
        Create a sky object of the Orion Nebula (M42) with custom styling:
        ```python
        m42 = SkyObject(
            name="M42",
            ra=5.58333,
            dec=-4.61,
            style={
                "marker": {
                    "size": 10,
                    "symbol": "s",
                    "fill": "full",
                    "color": "#ff6868",
                },
                "label": {
                    "font_size": 10,
                    "font_weight": "bold",
                    "font_color": "darkred",
                },
            },
        )
        ```
        Plot the object with [`MapPlot.plot_object()`][starplot.map.MapPlot.plot_object] or [`ZenithPlot.plot_object()`][starplot.zenith.ZenithPlot.plot_object]

    Args:
        name (str): Name of object (used for plotting its label)
        ra (flaot): Right ascension of object
        dec (flaot): Declination of object
        style (ObjectStyle): Styling for object
    """

    name: str
    ra: float
    dec: float
    style: ObjectStyle = ObjectStyle()
