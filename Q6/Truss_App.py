#region imports
import sys

from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw

from Truss_Classes import TrussController
from Truss_GUI import Ui_TrussStructuralDesign
#endregion


#region class definitions
class MainWindow(Ui_TrussStructuralDesign, qtw.QWidget):
    # Chat GPT helped me write this function.
    def __init__(self):
        """
        Build the main truss GUI and connect user actions to the controller.

        Args:
            None.

        Returns:
            None.
        """
        super().__init__()
        self.setupUi(self)

        self.controller = TrussController()
        self.controller.set_display_widgets(
            (
                self.te_DesignReport,
                self.le_LinkName,
                self.le_Node1Name,
                self.le_Node2Name,
                self.le_LinkLength,
                self.gv_Main,
            )
        )

        self.btn_Open.clicked.connect(self.open_file)
        self.spnd_Zoom.valueChanged.connect(self.set_zoom)

        # Keep all scene access behind the controller.
        self.controller.install_scene_event_filter(self)
        self.gv_Main.setMouseTracking(True)

        self.show()

    # Chat GPT helped me write this function.
    def set_zoom(self):
        """
        Apply the selected zoom factor to the graphics view.

        Args:
            None.

        Returns:
            None.
        """
        self.gv_Main.resetTransform()
        self.gv_Main.scale(self.spnd_Zoom.value(), self.spnd_Zoom.value())

    # Chat GPT helped me write this function.
    def eventFilter(self, obj, event):
        """
        Track scene mouse movement and wheel zoom events for the truss drawing.

        Args:
            obj: Qt object that received the event.
            event: Qt event object being filtered.

        Returns:
            True if the event is fully handled, otherwise the parent event result.
        """
        if self.controller.is_scene(obj):
            event_type = event.type()

            if event_type == qtc.QEvent.GraphicsSceneMouseMove:
                mouse_text = self.controller.mouse_position_text(
                    event.scenePos(),
                    self.gv_Main.transform(),
                )
                self.lbl_MousePos.setText(mouse_text)

            if event_type == qtc.QEvent.GraphicsSceneWheel:
                if event.delta() > 0:
                    self.spnd_Zoom.stepUp()
                else:
                    self.spnd_Zoom.stepDown()

        return super(MainWindow, self).eventFilter(obj, event)

    # Chat GPT helped me write this function.
    def open_file(self):
        """
        Ask the user for a truss input file and send its text to the controller.

        Args:
            None.

        Returns:
            None.
        """
        file_name = qtw.QFileDialog.getOpenFileName()[0]
        if len(file_name) == 0:
            return

        self.te_Path.setText(file_name)
        with open(file_name, "r") as input_file:
            file_data = input_file.readlines()

        self.controller.import_from_file(file_data)
#endregion


#region function definitions
# Chat GPT helped me write this function.
def main():
    """
    Start the Qt application and show the truss window.

    Args:
        None.

    Returns:
        None.
    """
    app = qtw.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec())
#endregion


#region function calls
if __name__ == "__main__":
    main()
#endregion
