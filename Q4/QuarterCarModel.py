#region imports
import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from scipy.integrate import odeint
from scipy.optimize import minimize
#endregion


#region constants
GRAVITY = 9.81
RAMP_HEIGHT_METERS = 6.0 / (12.0 * 3.3)
SAMPLE_COUNT = 2000
MIN_DAMPING = 10.0
BOUND_SCALE_LOW = 0.25
BOUND_SCALE_HIGH = 4.0
OPTIMIZATION_PENALTY = 100.0
LARGE_PENALTY = 1_000_000.0
#endregion


#region specialized graphic items
class MassBlock(qtw.QGraphicsItem):
    """Rectangle used to draw a mass in the schematic."""

    def __init__(
        self,
        center_x,
        center_y,
        width=30,
        height=10,
        parent=None,
        pen=None,
        brush=None,
        name="Car Body",
        mass=10,
    ):
        # Chat GPT helped me write this function.
        """
        Create a rectangular mass item for the graphics scene.

        Args:
            center_x: Horizontal center position of the mass.
            center_y: Vertical center position of the mass.
            width: Width of the mass rectangle.
            height: Height of the mass rectangle.
            parent: Optional parent graphics item.
            pen: Optional outline pen.
            brush: Optional fill brush.
            name: Display name for the tooltip.
            mass: Mass value shown in the tooltip.

        Returns:
            None.
        """
        super().__init__(parent)
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.pen = pen
        self.brush = brush
        self.name = name
        self.mass = mass
        self.rect = qtc.QRectF(-width / 2.0, -height / 2.0, width, height)

        self.setPos(center_x, center_y)
        self.setToolTip(
            f"{self.name}\n"
            f"x = {self.center_x:0.3f}, y = {self.center_y:0.3f}\n"
            f"mass = {self.mass:0.3f}"
        )

    def boundingRect(self):
        # Chat GPT helped me write this function.
        """
        Provide the item bounds required by QGraphicsItem.

        Args:
            None.

        Returns:
            QRectF: Rectangle containing the mass block.
        """
        return self.rect

    def paint(self, painter, option, widget=None):
        # Chat GPT helped me write this function.
        """
        Draw the mass block in the graphics scene.

        Args:
            painter: Qt painter used to draw the item.
            option: Qt style options for the item.
