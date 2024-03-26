from typing import Optional

from pydantic import BaseModel

from starplot.data.dsos import DsoType


class Star(BaseModel):
    """
    Star model. An instance of this model is passed to any [callables](/reference-callables) you define when plotting stars.
    So, you can use any attributes of this model in your callables. Note that some may be null.
    """

    ra: float
    """Right Ascension, in hours (0...24)"""

    dec: float
    """Declination, in degrees (-90...90)"""

    magnitude: float
    """Magnitude"""

    bv: Optional[float] = None
    """B-V Color Index, if available"""

    hip: Optional[int] = None
    """Hipparcos Catalog ID, if available"""

    name: Optional[str] = None
    """Name, if available"""


class DSO(BaseModel):
    """
    Deep Sky Object (DSO) model. An instance of this model is passed to any [callables](/reference-callables) you define when plotting DSOs.
    So, you can use any attributes of this model in your callables. Note that some may be null.
    """

    name: str
    """Name of the DSO (as specified in OpenNGC)"""

    ra: float
    """Right Ascension, in hours (0...24)"""

    dec: float
    """Declination, in degrees (-90...90)"""

    magnitude: Optional[float] = None
    """Magnitude (if available)"""

    type: DsoType

    maj_ax: Optional[float] = None
    """Major axis of the DSO, in arcmin (if available)"""

    min_ax: Optional[float] = None
    """Minor axis of the DSO, in arcmin (if available)"""

    angle: Optional[float] = None
    """Angle of the DSO, in degrees (if available)"""

    size: Optional[float] = None
    """Size of the DSO in degrees squared (if available)"""


class SkyObject(BaseModel):
    """
    Basic sky object model.
    """

    name: str
    """Name of the object"""

    ra: float
    """Right Ascension, in hours (0...24)"""

    dec: float
    """Declination, in degrees (-90...90)"""


class Planet(SkyObject):
    pass
