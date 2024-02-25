from typing import Optional

from pydantic import BaseModel


class SkyObject(BaseModel):
    pass


class Star(BaseModel):
    """
    Star model. An instance of this model is passed to any [callables](/reference-callables) you define when plotting stars.
    So, you can use any attributes of this model in your callables. Note that some may be null.
    """

    ra: float
    """Right Ascension"""

    dec: float
    """Declination"""

    magnitude: float
    """Magnitude"""

    bv: Optional[float] = None
    """B-V Color Index, if available"""

    hip: Optional[int] = None
    """Hipparcos Catalog ID, if available"""
