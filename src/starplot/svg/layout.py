from dataclasses import dataclass, field

from starplot.svg.elements import Element, Group, SVG
# from starplot.styles import TitleStyle, LegendStyle, PathStyle

@dataclass
class Border:
    pass

    """
    should take list of coordinates for labels:

    [
        ([(x1,y1), (x2,y2)], "north"),
        ([(x1,y1), (x2,y2)], "10"),
    ]
    
    coordinates are lines to intersect with border. Label plotted at intersection point

    """

@dataclass
class Region:
    elements: list[tuple[int, Element]] = field(default_factory=list)
    height: int = 0
    width: int = 0

    @property
    def is_empty(self):
        return bool(self.elements and self.height and self.width)

    def clear(self):
        self.elements = []
        self.height = 0
        self.width = 0
    
    def render(self):
        pass


@dataclass
class AxesRegion(Region):
    defs: list = field(default_factory=list)
    border: Region = field(default_factory=Region)
    footer: Region = field(default_factory=Footer)

    def render(self):
        pass



@dataclass
class Layout:
    axes: AxesRegion = field(default_factory=AxesRegion)
    # axes_border: Region = field(default_factory=Region)
    # axes_footer: Region = field(default_factory=Region)
    title: Region = field(default_factory=Region)
    legend: Region = field(default_factory=Region)
    tables: Region = field(default_factory=Region)

    def render(self):
        """
        Renders each region

        This function is responsible for determining the transform() for each region
        """

        pass
