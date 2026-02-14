from matplotlib.patches import Rectangle
from matplotlib.transforms import Bbox


class DebugPlotterMixin:
    def _debug_bbox(self, bbox, color, width=1):
        bboxe = Bbox([[bbox[0], bbox[1]], [bbox[2], bbox[3]]])
        bboxe = bboxe.transformed(self.ax.transAxes.inverted())
        rect = Rectangle(
            (bboxe.x0, bboxe.y0),  # (x, y) position in display pixels
            width=bboxe.width,
            height=bboxe.height,
            transform=self.ax.transAxes,
            fill=False,
            facecolor="none",
            edgecolor=color,
            linewidth=width,
            alpha=1,
            zorder=100_000,
        )
        self.ax.add_patch(rect)
