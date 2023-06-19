from pydantic import BaseModel

from starplot.styles import ObjectStyle


class SkyObject(BaseModel):
    """
    Model for plotting additional objects (e.g. DSOs)
    """

    name: str
    ra: float
    dec: float
    style: ObjectStyle = ObjectStyle()
