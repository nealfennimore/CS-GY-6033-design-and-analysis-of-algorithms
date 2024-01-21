from enum import Enum

import matplotlib.colors as mcolors

colors = mcolors.get_named_colors_mapping()


class Color(Enum):
    WHITE = colors["white"]
    BLACK = "black"
    SILVER = "silver"
    GREY = "grey"
    SANDYBROWN = "sandybrown"
    LIGHTSKYBLUE = "lightskyblue"
    SKYBLUE = "skyblue"
    DEEPSKYBLUE = "deepskyblue"
    GOLD = "gold"
    VIOLET = "violet"
    LIMEGREEN = "limegreen"
    DARKORANGE = "darkorange"


class NodeLabelColor(Enum):
    FONT = Color.BLACK.value
    BG = Color.SANDYBROWN.value


class NodeColor(Enum):
    DEFAULT = Color.SILVER.value
    VISITED = Color.DEEPSKYBLUE.value
    START_FROM = Color.LIGHTSKYBLUE.value
    FONT_COLOR = Color.BLACK.value


class EdgeLabelColor(Enum):
    FONT = Color.BLACK.value


class EdgeColor(Enum):
    LINE_DEFAULT = Color.GREY.value
    LINE_VISITED = Color.DARKORANGE.value
