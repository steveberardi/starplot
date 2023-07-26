from pydantic import BaseModel

from starplot.styles import ObjectStyle


class SkyObject(BaseModel):
    """
    Model for plotting additional objects (e.g. DSOs)

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
