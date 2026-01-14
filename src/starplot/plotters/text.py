from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional, Callable
import numpy as np


class CollisionAction(Enum):
    """What to do when a collision is detected."""
    ALLOW = "allow"          # Plot anyway, ignore collision
    REJECT = "reject"        # Don't plot the label
    RETRY = "retry"          # Try alternative positions
    PREVENT = "prevent"


class FallbackAction(Enum):
    """What to do when max retries exceeded and no good spot found."""
    PLOT_ANYWAY = "plot_anyway"      # Place at last attempted position
    PLOT_ORIGINAL = "plot_original"  # Place at original position
    SKIP = "skip"                    # Don't plot at all
    PLOT_BEST = "plot_best"          # Plot at position with least collision




class CollisionType(Enum):
    LABEL = "label"
    STAR = "star"
    CONSTELLATION_LINE = "constellation"
    OTHER_LINE = "line"


# remove_on_collision=True,
# remove_on_clipped=True,
# remove_on_constellation_collision=True,

# CollisionConfig
# avoid_clipped=True,
# avoid_label_collisions=True,
# avoid_marker_collisions=True,
# avoid_constellation_collision=True,
# on_fail: plot, skip


class CollisionHandler:
    allow_clipped = False
    allow_label_collisions = False
    allow_marker_collisions = False
    allow_constellation_collisions = False

    plot_on_fail = False



"""

Long term strategy:

- plot all markers FIRST (but keep track of labels)
- on export, find best positions for labels
- introduce some "priority" for labels (e.g. order by)

"""


class CollisionHandler:
    on_label = CollisionAction.REJECT
    on_star = CollisionAction.REJECT
    on_clipped = CollisionAction.REJECT
    on_constellation = CollisionAction.PREVENT

    fallback = FallbackAction.PLOT_BEST
    
    attempts = 100

    def positions(target, text, style):
        pass
        # yields a position to try + style (which could be adjusted with padding, font size, etc)

