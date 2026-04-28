#region imports
import sys

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5 import QtCore
from PyQt5 import QtWidgets as qtw

from cycle_model import AirStandardCycleModel, CycleInputs
#endregion


#region constants
ATM_TO_PA = 101325.0
FT3_PER_M3 = 35.3146667215
J_PER_BTU = 1055.06
RANKINE_PER_KELVIN = 9.0 / 5.0
#endregion


#region view
class CycleView(qtw.QWidget):
    """
    Builds and updates the PyQt GUI for the cycle calculator.

    Args:
        None.

    Returns:
        A QWidget-based view object.
    """

    # Chat GPT helped me write this function.
    def __init__(self):
        """
        Creates all widgets and prepares the window.

        Args:
            None.

        Returns:
            None.
        """
        super().__init__()
        self.state_row_widgets = []
        self.temperature_outputs = []
        self.pressure_outputs = []
        self.temperature_unit_labels = []
        self.pressure_unit_labels = []
        self.result_outputs = {}
        self.result_unit_labels = {}
        self._build_ui()
        self.set_cycle_labels("Otto", True)
        self.clear_outputs()

    # Chat GPT helped me write this function.
    def _build_ui(self):
        """
        Builds the main layout and all GUI sections.

        Args:
            None.

        Returns:
            None.
        """
        self.setWindowTitle("Air Standard Otto, Diesel, and Dual Cycle Calculator")
        self.resize(1200, 900)
        main_layout = qtw.QVBoxLayout(self)
        main_layout.addWidget(self._build_input_group())
        main_layout.addWidget(self._build_output_group())
        main_layout.addWidget(self._build_plot_group())

        self.figure = Figure(figsize=(9, 5), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(111)
        main_layout.addWidget(self.canvas, stretch=1)

    # Chat GPT helped me write this function.
    def _build_input_group(self):
        """
        Creates the input widgets for the selected cycle.

        Args:
            None.

        Returns:
            A QGroupBox containing the input controls.
        """
        self.gb_input = qtw.QGroupBox("Input")
        input_layout = qtw.QGridLayout(self.gb_input)

        self.cmb_cycle = qtw.QComboBox()
        self.cmb_cycle.addItems(["Otto", "Diesel", "Dual"])
        self.rdo_si = qtw.QRadioButton("SI")
        self.rdo_english = qtw.QRadioButton("English")
        self.rdo_si.setChecked(True)

        self.le_temperature_1 = self._make_line_edit("300", "le_temperature_1")
        self.le_pressure_1 = self._make_line_edit("100", "le_pressure_1")
        self.le_volume_1 = self._make_line_edit("0.003", "le_volume_1")
        self.le_compression_ratio = self._make_line_edit("8", "le_compression_ratio")
        self.le_primary_parameter = self._make_line_edit("1800", "le_primary_parameter")
        self.le_secondary_parameter = self._make_line_edit("1.2", "le_secondary_parameter")

        self.lbl_temperature_1 = qtw.QLabel()
        self.lbl_pressure_1 = qtw.QLabel()
        self.lbl_volume_1 = qtw.QLabel()
        self.lbl_compression_ratio = qtw.QLabel("Compression Ratio")
        self.lbl_primary_parameter = qtw.QLabel()
        self.lbl_secondary_parameter = qtw.QLabel()
        self.btn_calculate = qtw.QPushButton("Calculate")

        input_layout.addWidget(qtw.QLabel("Cycle"), 0, 0, alignment=QtCore.Qt.AlignRight)
        input_layout.addWidget(self.cmb_cycle, 0, 1)
        input_layout.addWidget(self.rdo_si, 0, 2)
        input_layout.addWidget(self.rdo_english, 0, 3)
        input_layout.addWidget(self.lbl_temperature_1, 1, 0, alignment=QtCore.Qt.AlignRight)
        input_layout.addWidget(self.le_temperature_1, 1, 1)
        input_layout.addWidget(self.lbl_pressure_1, 2, 0, alignment=QtCore.Qt.AlignRight)
        input_layout.addWidget(self.le_pressure_1, 2, 1)
        input_layout.addWidget(self.lbl_volume_1, 3, 0, alignment=QtCore.Qt.AlignRight)
        input_layout.addWidget(self.le_volume_1, 3, 1)
        input_layout.addWidget(self.lbl_compression_ratio, 4, 0, alignment=QtCore.Qt.AlignRight)
        input_layout.addWidget(self.le_compression_ratio, 4, 1)
        input_layout.addWidget(self.lbl_primary_parameter, 1, 2, alignment=QtCore.Qt.AlignRight)
        input_layout.addWidget(self.le_primary_parameter, 1, 3)
        input_layout.addWidget(self.lbl_secondary_parameter, 2, 2, alignment=QtCore.Qt.AlignRight)
        input_layout.addWidget(self.le_secondary_parameter, 2, 3)
        input_layout.addWidget(self.btn_calculate, 4, 2, 1, 2)
        input_layout.setColumnStretch(4, 1)
        return self.gb_input

    # Chat GPT helped me write this function.
    def _build_output_group(self):
        """
        Creates the output widgets for states and cycle performance.

        Args:
            None.

        Returns:
            A QGroupBox containing output line edits.
        """
        output_group = qtw.QGroupBox("Output")
        output_layout = qtw.QGridLayout(output_group)

        output_layout.addWidget(qtw.QLabel("State"), 0, 0)
        output_layout.addWidget(qtw.QLabel("Temperature"), 0, 1)
        output_layout.addWidget(qtw.QLabel("Pressure"), 0, 3)
        for state_number in range(1, 6):
            state_label = qtw.QLabel(f"T{state_number}, P{state_number}")
            temperature_output = self._make_line_edit("", f"le_T{state_number}", read_only=True)
            pressure_output = self._make_line_edit("", f"le_P{state_number}", read_only=True)
            temperature_unit = qtw.QLabel()
            pressure_unit = qtw.QLabel()
            row = state_number
            row_widgets = [state_label, temperature_output, temperature_unit, pressure_output, pressure_unit]
            output_layout.addWidget(state_label, row, 0)
            output_layout.addWidget(temperature_output, row, 1)
            output_layout.addWidget(temperature_unit, row, 2)
            output_layout.addWidget(pressure_output, row, 3)
            output_layout.addWidget(pressure_unit, row, 4)
            self.state_row_widgets.append(row_widgets)
            self.temperature_outputs.append(temperature_output)
            self.pressure_outputs.append(pressure_output)
            self.temperature_unit_labels.append(temperature_unit)
            self.pressure_unit_labels.append(pressure_unit)

        result_names = [
            ("compression_work", "Compression Work"),
            ("power_work", "Power Stroke Work"),
            ("net_work", "Net Work"),
            ("heat_added", "Heat Added"),
            ("heat_rejected", "Heat Rejected"),
            ("efficiency", "Cycle Efficiency"),
        ]
        for row_offset, result_item in enumerate(result_names, start=1):
            key, label_text = result_item
            label = qtw.QLabel(label_text)
            line_edit = self._make_line_edit("", f"le_{key}", read_only=True)
            unit_label = qtw.QLabel()
            output_layout.addWidget(label, row_offset, 6, alignment=QtCore.Qt.AlignRight)
            output_layout.addWidget(line_edit, row_offset, 7)
            output_layout.addWidget(unit_label, row_offset, 8)
            self.result_outputs[key] = line_edit
            self.result_unit_labels[key] = unit_label

        output_layout.setColumnStretch(5, 1)
        return output_group

    # Chat GPT helped me write this function.
    def _build_plot_group(self):
        """
        Creates the plot control widgets.

        Args:
            None.

        Returns:
            A QGroupBox containing plot controls.
        """
        plot_group = qtw.QGroupBox("Plot")
        plot_layout = qtw.QGridLayout(plot_group)
        self.cmb_x_property = qtw.QComboBox()
        self.cmb_y_property = qtw.QComboBox()
        self.cmb_x_property.addItems(["P", "T", "u", "h", "s", "v"])
        self.cmb_y_property.addItems(["P", "T", "u", "h", "s", "v"])
        self.cmb_x_property.setCurrentText("v")
        self.cmb_y_property.setCurrentText("P")
        self.chk_log_x = qtw.QCheckBox("Log x")
        self.chk_log_y = qtw.QCheckBox("Log y")

        plot_layout.addWidget(qtw.QLabel("X Axis"), 0, 0, alignment=QtCore.Qt.AlignRight)
        plot_layout.addWidget(self.cmb_x_property, 0, 1)
        plot_layout.addWidget(qtw.QLabel("Y Axis"), 0, 2, alignment=QtCore.Qt.AlignRight)
        plot_layout.addWidget(self.cmb_y_property, 0, 3)
        plot_layout.addWidget(self.chk_log_x, 1, 1)
        plot_layout.addWidget(self.chk_log_y, 1, 3)
        plot_layout.setColumnStretch(4, 1)
        return plot_group

    # Chat GPT helped me write this function.
    def _make_line_edit(self, text, object_name, read_only=False):
        """
        Creates a consistently formatted line edit.

        Args:
            text: Initial text for the line edit.
            object_name: Qt object name for easier grading and debugging.
            read_only: True when the user should not edit the value.

        Returns:
            A configured QLineEdit object.
        """
        line_edit = qtw.QLineEdit(text)
        line_edit.setObjectName(object_name)
        line_edit.setMaximumWidth(180)
        line_edit.setReadOnly(read_only)
        if read_only:
            line_edit.setStyleSheet("background-color: #f5f5f5;")
        return line_edit

    # Chat GPT helped me write this function.
    def set_cycle_labels(self, cycle_type, si_units):
        """
        Updates labels and visible inputs for the selected cycle and unit system.

        Args:
            cycle_type: Selected cycle name.
            si_units: True for SI labels, False for English labels.

        Returns:
            None.
        """
        temperature_unit = "K" if si_units else "R"
        pressure_unit = "kPa" if si_units else "atm"
        volume_unit = "m^3" if si_units else "ft^3"
        self.gb_input.setTitle(f"Input for Air Standard {cycle_type} Cycle")
        self.lbl_temperature_1.setText(f"T1 ({temperature_unit})")
        self.lbl_pressure_1.setText(f"P1 ({pressure_unit})")
        self.lbl_volume_1.setText(f"V1 at BDC ({volume_unit})")

        if cycle_type == "Otto":
            self.lbl_primary_parameter.setText(f"T3 High ({temperature_unit})")
            self.lbl_secondary_parameter.hide()
            self.le_secondary_parameter.hide()
        elif cycle_type == "Diesel":
            self.lbl_primary_parameter.setText("Cutoff Ratio rc")
            self.lbl_secondary_parameter.hide()
            self.le_secondary_parameter.hide()
        else:
            self.lbl_primary_parameter.setText("Pressure Ratio P3/P2")
            self.lbl_secondary_parameter.setText("Cutoff Ratio rc")
            self.lbl_secondary_parameter.show()
            self.le_secondary_parameter.show()

    # Chat GPT helped me write this function.
    def set_input_values(self, values):
        """
        Writes display-unit input values into the GUI.

        Args:
            values: Dictionary of input names and display-unit values.

        Returns:
            None.
        """
        self.le_temperature_1.setText(f"{values['temperature_1']:.6g}")
        self.le_pressure_1.setText(f"{values['pressure_1']:.6g}")
        self.le_volume_1.setText(f"{values['volume_1']:.6g}")
        self.le_compression_ratio.setText(f"{values['compression_ratio']:.6g}")
        self.le_primary_parameter.setText(f"{values['primary_value']:.6g}")
        self.le_secondary_parameter.setText(f"{values['secondary_value']:.6g}")

    # Chat GPT helped me write this function.
    def read_inputs(self):
        """
        Reads all visible GUI input values.

        Args:
            None.

        Returns:
            A dictionary with numeric input values in the displayed units.
        """
        return {
            "cycle_type": self.selected_cycle(),
            "temperature_1": self._line_value(self.le_temperature_1, "T1"),
            "pressure_1": self._line_value(self.le_pressure_1, "P1"),
            "volume_1": self._line_value(self.le_volume_1, "V1"),
            "compression_ratio": self._line_value(self.le_compression_ratio, "compression ratio"),
            "primary_value": self._line_value(self.le_primary_parameter, self.lbl_primary_parameter.text()),
            "secondary_value": self._line_value(self.le_secondary_parameter, self.lbl_secondary_parameter.text()) if self.le_secondary_parameter.isVisible() else 1.0,
        }

    # Chat GPT helped me write this function.
    def _line_value(self, line_edit, value_name):
        """
        Converts one line edit value to a float.

        Args:
            line_edit: QLineEdit to read.
            value_name: Friendly name for error messages.

        Returns:
            The line edit value as a float.
        """
        try:
            return float(line_edit.text())
        except ValueError as exc:
            raise ValueError(f"{value_name} must be a number.") from exc

    # Chat GPT helped me write this function.
    def is_si_units(self):
        """
        Reports whether the SI radio button is selected.

        Args:
            None.

        Returns:
            True for SI units and False for English units.
        """
        return self.rdo_si.isChecked()

    # Chat GPT helped me write this function.
    def selected_cycle(self):
        """
        Gets the currently selected cycle name.

        Args:
            None.

        Returns:
            Selected cycle text from the combo box.
        """
        return self.cmb_cycle.currentText()

    # Chat GPT helped me write this function.
    def display_results(self, results, si_units):
        """
        Writes calculated states and performance results to the GUI.

        Args:
            results: CycleResults object from the model.
            si_units: True for SI output units, False for English output units.

        Returns:
            None.
        """
        temperature_unit = "K" if si_units else "R"
        pressure_unit = "kPa" if si_units else "atm"
        energy_unit = "kJ" if si_units else "Btu"
        state_count = len(results.states)

        for index in range(5):
            visible = index < state_count
            for widget in self.state_row_widgets[index]:
                widget.setVisible(visible)
            if visible:
                state = results.states[index]
                self.temperature_outputs[index].setText(f"{self._converted_state_value(state, 'T', results.moles, si_units):.4g}")
                self.pressure_outputs[index].setText(f"{self._converted_state_value(state, 'P', results.moles, si_units):.4g}")
                self.temperature_unit_labels[index].setText(temperature_unit)
                self.pressure_unit_labels[index].setText(pressure_unit)

        self.result_outputs["compression_work"].setText(f"{self._total_energy(results.compression_work, results.moles, si_units):.4g}")
        self.result_outputs["power_work"].setText(f"{self._total_energy(results.power_work, results.moles, si_units):.4g}")
        self.result_outputs["net_work"].setText(f"{self._total_energy(results.net_work, results.moles, si_units):.4g}")
        self.result_outputs["heat_added"].setText(f"{self._total_energy(results.heat_added, results.moles, si_units):.4g}")
        self.result_outputs["heat_rejected"].setText(f"{self._total_energy(results.heat_rejected, results.moles, si_units):.4g}")
        self.result_outputs["efficiency"].setText(f"{results.efficiency:.3f}")

        for key in ["compression_work", "power_work", "net_work", "heat_added", "heat_rejected"]:
            self.result_unit_labels[key].setText(energy_unit)
        self.result_unit_labels["efficiency"].setText("%")

    # Chat GPT helped me write this function.
    def clear_outputs(self):
        """
        Clears all output fields and resets the plot.

        Args:
            None.

        Returns:
            None.
        """
        for line_edit in self.temperature_outputs + self.pressure_outputs:
            line_edit.clear()
        for line_edit in self.result_outputs.values():
            line_edit.clear()
        self.axes.clear()
        self.axes.set_title("Cycle plot will appear after calculation")
        self.canvas.draw()

    # Chat GPT helped me write this function.
    def show_error(self, message):
        """
        Shows a user-friendly error message.

        Args:
            message: Text to display in the message box.

        Returns:
            None.
        """
        qtw.QMessageBox.warning(self, "Input Error", message)

    # Chat GPT helped me write this function.
    def draw_plot(self, results, si_units):
        """
        Draws the selected thermodynamic plot on the embedded canvas.

        Args:
            results: CycleResults object from the model.
            si_units: True for SI plot units, False for English plot units.

        Returns:
            None.
        """
        x_property = self.cmb_x_property.currentText()
        y_property = self.cmb_y_property.currentText()
        self.axes.clear()

        if x_property == y_property:
            self.axes.set_title("Choose different properties for x and y")
            self.canvas.draw()
            return

        for process in results.processes:
            x_values = [self._converted_state_value(state, x_property, results.moles, si_units) for state in process.states]
            y_values = [self._converted_state_value(state, y_property, results.moles, si_units) for state in process.states]
            self.axes.plot(x_values, y_values, linewidth=2, label=process.name)

        for index, state in enumerate(results.states, start=1):
            x_value = self._converted_state_value(state, x_property, results.moles, si_units)
            y_value = self._converted_state_value(state, y_property, results.moles, si_units)
            self.axes.plot(x_value, y_value, marker="o", markerfacecolor="white", markeredgecolor="black")
            self.axes.annotate(str(index), (x_value, y_value), textcoords="offset points", xytext=(6, 6))

        if self.chk_log_x.isChecked():
            self.axes.set_xscale("log")
        if self.chk_log_y.isChecked():
            self.axes.set_yscale("log")
        self.axes.set_xlabel(self._property_axis_label(x_property, si_units))
        self.axes.set_ylabel(self._property_axis_label(y_property, si_units))
        self.axes.set_title(f"Air Standard {results.cycle_type} Cycle")
        self.axes.grid(True, alpha=0.25)
        self.axes.legend(fontsize="small")
        self.canvas.draw()

    # Chat GPT helped me write this function.
    def _converted_state_value(self, state, property_name, moles, si_units):
        """
        Converts one state property into the selected display units.

        Args:
            state: StatePoint object to convert.
            property_name: One of P, T, u, h, s, or v.
            moles: Amount of air in the cylinder in mol.
            si_units: True for SI units, False for English units.

        Returns:
            Converted property value for display or plotting.
        """
        property_key = property_name.lower()
        if property_key == "p":
            return state.pressure / 1000.0 if si_units else state.pressure / ATM_TO_PA
        if property_key == "t":
            return state.temperature if si_units else state.temperature * RANKINE_PER_KELVIN
        if property_key == "v":
            total_volume = state.specific_volume * moles
            return total_volume if si_units else total_volume * FT3_PER_M3
        if property_key == "u":
            return self._total_energy(state.internal_energy, moles, si_units)
        if property_key == "h":
            return self._total_energy(state.enthalpy, moles, si_units)
        if property_key == "s":
            return self._total_entropy(state.entropy, moles, si_units)
        raise ValueError("Unknown property name.")

    # Chat GPT helped me write this function.
    def _property_axis_label(self, property_name, si_units):
        """
        Builds a plot axis label for the selected property and unit system.

        Args:
            property_name: One of P, T, u, h, s, or v.
            si_units: True for SI units, False for English units.

        Returns:
            Axis label text.
        """
        if si_units:
            labels = {
                "P": "P (kPa)",
                "T": "T (K)",
                "u": "U (kJ)",
                "h": "H (kJ)",
                "s": "S (kJ/K)",
                "v": "V (m^3)",
            }
        else:
            labels = {
                "P": "P (atm)",
                "T": "T (R)",
                "u": "U (Btu)",
                "h": "H (Btu)",
                "s": "S (Btu/R)",
                "v": "V (ft^3)",
            }
        return labels[property_name]

    # Chat GPT helped me write this function.
    def _total_energy(self, molar_energy, moles, si_units):
        """
        Converts molar energy to total displayed energy.

        Args:
            molar_energy: Energy per mole in J/mol.
            moles: Amount of air in mol.
            si_units: True for kJ, False for Btu.

        Returns:
            Total energy in kJ or Btu.
        """
        total_joules = molar_energy * moles
        return total_joules / 1000.0 if si_units else total_joules / J_PER_BTU

    # Chat GPT helped me write this function.
    def _total_entropy(self, molar_entropy, moles, si_units):
        """
        Converts molar entropy to total displayed entropy.

        Args:
            molar_entropy: Entropy per mole in J/(mol*K).
            moles: Amount of air in mol.
            si_units: True for kJ/K, False for Btu/R.

        Returns:
            Total entropy in kJ/K or Btu/R.
        """
        total_entropy_si = molar_entropy * moles
        return total_entropy_si / 1000.0 if si_units else total_entropy_si / (J_PER_BTU * RANKINE_PER_KELVIN)
#endregion


#region controller
class CycleController:
    """
    Connects the view with the thermodynamic cycle model.

    Args:
        view: CycleView object that owns the GUI widgets.
        model: AirStandardCycleModel object that performs calculations.

    Returns:
        A controller object that handles user actions.
    """

    # Chat GPT helped me write this function.
    def __init__(self, view, model):
        """
        Stores model and view references and connects GUI signals.

        Args:
            view: CycleView object.
            model: AirStandardCycleModel object.

        Returns:
            None.
        """
        self.view = view
        self.model = model
        self.using_si = self.view.is_si_units()
        self._connect_signals()
        self._load_defaults("Otto")

    # Chat GPT helped me write this function.
    def _connect_signals(self):
        """
        Connects user interface events to controller methods.

        Args:
            None.

        Returns:
            None.
        """
        self.view.cmb_cycle.currentIndexChanged.connect(self.handle_cycle_change)
        self.view.rdo_si.toggled.connect(self.handle_units_change)
        self.view.btn_calculate.clicked.connect(self.calculate_cycle)
        self.view.cmb_x_property.currentIndexChanged.connect(self.update_plot)
        self.view.cmb_y_property.currentIndexChanged.connect(self.update_plot)
        self.view.chk_log_x.stateChanged.connect(self.update_plot)
        self.view.chk_log_y.stateChanged.connect(self.update_plot)

    # Chat GPT helped me write this function.
    def _load_defaults(self, cycle_type):
        """
        Loads example values for the chosen cycle.

        Args:
            cycle_type: Selected cycle name.

        Returns:
            None.
        """
        default_inputs = self._default_si_inputs(cycle_type)
        self.view.set_cycle_labels(cycle_type, self.using_si)
        self.view.set_input_values(self._display_values_from_si_inputs(default_inputs, self.using_si))
        self.view.clear_outputs()

    # Chat GPT helped me write this function.
    def handle_cycle_change(self):
        """
        Responds when the user selects Otto, Diesel, or Dual.

        Args:
            None.

        Returns:
            None.
        """
        self._load_defaults(self.view.selected_cycle())

    # Chat GPT helped me write this function.
    def handle_units_change(self):
        """
        Converts existing inputs when the unit radio button changes.

        Args:
            None.

        Returns:
            None.
        """
        new_si = self.view.is_si_units()
        if new_si == self.using_si:
            return

        cycle_type = self.view.selected_cycle()
        try:
            raw_values = self.view.read_inputs()
            si_inputs = self._si_inputs_from_display_values(raw_values, self.using_si)
            display_values = self._display_values_from_si_inputs(si_inputs, new_si)
            self.using_si = new_si
            self.view.set_cycle_labels(cycle_type, self.using_si)
            self.view.set_input_values(display_values)
            if self.model.results is not None:
                self.view.display_results(self.model.results, self.using_si)
                self.view.draw_plot(self.model.results, self.using_si)
        except ValueError:
            self.using_si = new_si
            self._load_defaults(cycle_type)

    # Chat GPT helped me write this function.
    def calculate_cycle(self):
        """
        Reads inputs, updates the model, and refreshes GUI outputs.

        Args:
            None.

        Returns:
            None.
        """
        try:
            raw_values = self.view.read_inputs()
            si_inputs = self._si_inputs_from_display_values(raw_values, self.using_si)
            results = self.model.calculate(si_inputs)
            self.view.display_results(results, self.using_si)
            self.view.draw_plot(results, self.using_si)
            print(self._format_summary(results, self.using_si))
        except ValueError as exc:
            self.view.show_error(str(exc))

    # Chat GPT helped me write this function.
    def update_plot(self):
        """
        Replots the most recent calculated cycle.

        Args:
            None.

        Returns:
            None.
        """
        if self.model.results is not None:
            self.view.draw_plot(self.model.results, self.using_si)

    # Chat GPT helped me write this function.
    def _si_inputs_from_display_values(self, values, si_units):
        """
        Converts GUI display-unit values into SI model inputs.

        Args:
            values: Dictionary of GUI values.
            si_units: True if the values are already in SI display units.

        Returns:
            CycleInputs object with model-ready SI values.
        """
        cycle_type = values["cycle_type"]
        temperature_1 = values["temperature_1"] if si_units else values["temperature_1"] / RANKINE_PER_KELVIN
        pressure_1 = values["pressure_1"] * 1000.0 if si_units else values["pressure_1"] * ATM_TO_PA
        volume_1 = values["volume_1"] if si_units else values["volume_1"] / FT3_PER_M3
        compression_ratio = values["compression_ratio"]
        primary_value = values["primary_value"]
        secondary_value = values["secondary_value"]

        if cycle_type == "Otto":
            temperature_high = primary_value if si_units else primary_value / RANKINE_PER_KELVIN
            cutoff_ratio = 2.0
            pressure_ratio = 1.5
        elif cycle_type == "Diesel":
            temperature_high = 1800.0
            cutoff_ratio = primary_value
            pressure_ratio = 1.5
        else:
            temperature_high = 1800.0
            cutoff_ratio = secondary_value
            pressure_ratio = primary_value

        return CycleInputs(
            cycle_type=cycle_type.lower(),
            temperature_1=temperature_1,
            pressure_1=pressure_1,
            volume_1=volume_1,
            compression_ratio=compression_ratio,
            temperature_high=temperature_high,
            cutoff_ratio=cutoff_ratio,
            pressure_ratio=pressure_ratio,
        )

    # Chat GPT helped me write this function.
    def _display_values_from_si_inputs(self, inputs, si_units):
        """
        Converts SI model inputs into GUI display-unit values.

        Args:
            inputs: CycleInputs object in SI units.
            si_units: True for SI display values, False for English display values.

        Returns:
            Dictionary of values ready for the GUI input fields.
        """
        temperature_1 = inputs.temperature_1 if si_units else inputs.temperature_1 * RANKINE_PER_KELVIN
        pressure_1 = inputs.pressure_1 / 1000.0 if si_units else inputs.pressure_1 / ATM_TO_PA
        volume_1 = inputs.volume_1 if si_units else inputs.volume_1 * FT3_PER_M3

        if inputs.cycle_type == "otto":
            primary_value = inputs.temperature_high if si_units else inputs.temperature_high * RANKINE_PER_KELVIN
            secondary_value = 1.2
        elif inputs.cycle_type == "diesel":
            primary_value = inputs.cutoff_ratio
            secondary_value = 1.2
        else:
            primary_value = inputs.pressure_ratio
            secondary_value = inputs.cutoff_ratio

        return {
            "temperature_1": temperature_1,
            "pressure_1": pressure_1,
            "volume_1": volume_1,
            "compression_ratio": inputs.compression_ratio,
            "primary_value": primary_value,
            "secondary_value": secondary_value,
        }

    # Chat GPT helped me write this function.
    def _default_si_inputs(self, cycle_type):
        """
        Builds default example inputs for the selected cycle.

        Args:
            cycle_type: Selected cycle name.

        Returns:
            CycleInputs object using SI units.
        """
        if cycle_type == "Otto":
            return CycleInputs("otto", 300.0, 100000.0, 0.003, 8.0, temperature_high=1800.0)
        if cycle_type == "Diesel":
            return CycleInputs("diesel", 300.0, 100000.0, 0.003, 18.0, cutoff_ratio=2.0)
        return CycleInputs("dual", 300.0, 100000.0, 0.003, 18.0, cutoff_ratio=1.2, pressure_ratio=1.5)

    # Chat GPT helped me write this function.
    def _format_summary(self, results, si_units):
        """
        Builds a clean console summary for graders.

        Args:
            results: CycleResults object to summarize.
            si_units: True for SI units, False for English units.

        Returns:
            Multiline summary string.
        """
        pressure_unit = "kPa" if si_units else "atm"
        temperature_unit = "K" if si_units else "R"
        energy_unit = "kJ" if si_units else "Btu"
        lines = [f"\nAir Standard {results.cycle_type} Cycle Results"]
        lines.append("State Results:")
        for index, state in enumerate(results.states, start=1):
            temperature = self.view._converted_state_value(state, "T", results.moles, si_units)
            pressure = self.view._converted_state_value(state, "P", results.moles, si_units)
            lines.append(f"  State {index}: T = {temperature:.3f} {temperature_unit}, P = {pressure:.3f} {pressure_unit}")
        lines.append("Cycle Performance:")
        lines.append(f"  Compression Work = {self.view._total_energy(results.compression_work, results.moles, si_units):.4g} {energy_unit}")
        lines.append(f"  Power Stroke Work = {self.view._total_energy(results.power_work, results.moles, si_units):.4g} {energy_unit}")
        lines.append(f"  Net Work = {self.view._total_energy(results.net_work, results.moles, si_units):.4g} {energy_unit}")
        lines.append(f"  Heat Added = {self.view._total_energy(results.heat_added, results.moles, si_units):.4g} {energy_unit}")
        lines.append(f"  Heat Rejected = {self.view._total_energy(results.heat_rejected, results.moles, si_units):.4g} {energy_unit}")
        lines.append(f"  Efficiency = {results.efficiency:.3f} %")
        return "\n".join(lines)
#endregion


#region main
# Chat GPT helped me write this function.
def main():
    """
    Starts the Qt application.

    Args:
        None.

    Returns:
        None.
    """
    app = qtw.QApplication(sys.argv)
    view = CycleView()
    CycleController(view, AirStandardCycleModel())
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
#endregion
