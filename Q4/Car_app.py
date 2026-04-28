#region imports
import sys

from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw

from Car_GUI import Ui_Form
from QuarterCarModel import CarController
#endregion


#region main window
class MainWindow(qtw.QWidget, Ui_Form):
    """Main application window for the quarter car model GUI."""

    def __init__(self):
        # Chat GPT helped me write this function.
        """
        Build the main window, create the controller, and connect GUI events.

        Args:
            None.

        Returns:
            None.
        """
        super().__init__()
        self.setupUi(self)

        self.controller = CarController(self._collect_widgets())
        self._connect_signals()
        self.show()

    def _collect_widgets(self):
        # Chat GPT helped me write this function.
        """
        Collect the input and display widgets that the controller needs.

        Args:
            None.

        Returns:
            tuple: Input widgets and display widgets grouped for the controller.
        """
        input_widgets = (
            self.le_m1,
            self.le_v,
            self.le_k1,
            self.le_c1,
            self.le_m2,
            self.le_k2,
            self.le_ang,
            self.le_tmax,
            self.chk_IncludeAccel,
        )
        display_widgets = (
            self.gv_Schematic,
            self.chk_LogX,
            self.chk_LogY,
            self.chk_LogAccel,
            self.chk_ShowAccel,
            self.lbl_MaxMinInfo,
            self.layout_horizontal_main,
        )
        return input_widgets, display_widgets

    def _connect_signals(self):
        # Chat GPT helped me write this function.
        """
        Connect GUI controls to the controller methods that handle them.

        Args:
            None.

        Returns:
            None.
        """
        self.btn_calculate.clicked.connect(lambda: self.controller.calculate())
        self.pb_Optimize.clicked.connect(lambda: self.do_optimize())

        # Replot when a display option changes.
        self.chk_LogX.stateChanged.connect(lambda: self.controller.plot_results())
        self.chk_LogY.stateChanged.connect(lambda: self.controller.plot_results())
        self.chk_LogAccel.stateChanged.connect(lambda: self.controller.plot_results())
        self.chk_ShowAccel.stateChanged.connect(lambda: self.controller.plot_results())

    def do_optimize(self):
        # Chat GPT helped me write this function.
        """
        Run the suspension optimizer while showing a wait cursor.

        Args:
            None.

        Returns:
            None.
        """
        qtw.QApplication.setOverrideCursor(qtc.Qt.WaitCursor)
        try:
            self.controller.optimize_suspension()
