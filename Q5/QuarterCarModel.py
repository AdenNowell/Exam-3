#region imports
import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
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
            widget: Optional widget receiving the drawing.

        Returns:
            None.
        """
        if self.pen is not None:
            painter.setPen(self.pen)
        if self.brush is not None:
            painter.setBrush(self.brush)
        painter.drawRect(self.rect)


class Wheel(qtw.QGraphicsItem):
    """Circle used to draw the wheel and its wheel mass."""

    def __init__(
        self,
        center_x,
        center_y,
        radius=10,
        parent=None,
        pen=None,
        wheel_brush=None,
        mass_brush=None,
        name="Wheel",
        mass=10,
    ):
        # Chat GPT helped me write this function.
        """
        Create a wheel item for the graphics scene.

        Args:
            center_x: Horizontal center position of the wheel.
            center_y: Vertical center position of the wheel.
            radius: Wheel radius.
            parent: Optional parent graphics item.
            pen: Optional outline pen.
            wheel_brush: Optional wheel fill brush.
            mass_brush: Optional wheel-mass fill brush.
            name: Display name for the tooltip.
            mass: Wheel mass shown in the tooltip.

        Returns:
            None.
        """
        super().__init__(parent)
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.pen = pen
        self.brush = wheel_brush
        self.name = name
        self.mass = mass
        self.rect = qtc.QRectF(-radius, -radius, radius * 2.0, radius * 2.0)
        self.mass_block = MassBlock(
            center_x,
            center_y,
            width=2.0 * radius * 0.85,
            height=radius / 3.0,
            pen=pen,
            brush=mass_brush,
            name="Wheel Mass",
            mass=mass,
        )

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
            QRectF: Rectangle containing the wheel.
        """
        return self.rect

    def add_to_scene(self, scene):
        # Chat GPT helped me write this function.
        """
        Add the wheel and wheel mass to a graphics scene.

        Args:
            scene: QGraphicsScene that receives the wheel items.

        Returns:
            None.
        """
        scene.addItem(self)
        scene.addItem(self.mass_block)

    def paint(self, painter, option, widget=None):
        # Chat GPT helped me write this function.
        """
        Draw the wheel in the graphics scene.

        Args:
            painter: Qt painter used to draw the item.
            option: Qt style options for the item.
            widget: Optional widget receiving the drawing.

        Returns:
            None.
        """
        if self.pen is not None:
            painter.setPen(self.pen)
        if self.brush is not None:
            painter.setBrush(self.brush)
        painter.drawEllipse(self.rect)
#endregion


#region model
class CarModel:
    """Store quarter-car inputs, limits, and calculated results."""

    def __init__(self):
        # Chat GPT helped me write this function.
        """
        Create a quarter-car model with general default values.

        Args:
            None.

        Returns:
            None.
        """
        self.tmax = 3.0
        self.time_data = np.linspace(0.0, self.tmax, SAMPLE_COUNT)
        self.ramp_time = 1.0
        self.ramp_angle_radians = 0.1
        self.ramp_height = RAMP_HEIGHT_METERS
        self.ramp_angle_degrees = 45.0

        self.m1 = 450.0
        self.m2 = 20.0
        self.c1 = 4500.0
        self.k1 = 15000.0
        self.k2 = 90000.0
        self.v = 120.0

        self.min_k1 = 0.0
        self.max_k1 = 0.0
        self.min_k2 = 0.0
        self.max_k2 = 0.0
        self.acceleration = None
        self.max_acceleration = 0.0
        self.acceleration_limit = 2.0
        self.suspension_spring_force = None
        self.dashpot_force = None
        self.tire_spring_force = None
        self.max_suspension_spring_force = 0.0
        self.max_dashpot_force = 0.0
        self.max_tire_spring_force = 0.0
        self.sum_square_error = 0.0
        self.results = None
        self.update_limits()

    def update_limits(self):
        # Chat GPT helped me write this function.
        """
        Recalculate optimization limits from the current spring constants.

        Args:
            None.

        Returns:
            None.
        """
        # The limits scale with the current inputs so different cars still work.
        self.min_k1 = max(self.k1 * BOUND_SCALE_LOW, 1.0)
        self.max_k1 = max(self.k1 * BOUND_SCALE_HIGH, self.min_k1 + 1.0)
        self.min_k2 = max(self.k2 * BOUND_SCALE_LOW, 1.0)
        self.max_k2 = max(self.k2 * BOUND_SCALE_HIGH, self.min_k2 + 1.0)

    def road_height_at_time(self, time_value):
        # Chat GPT helped me write this function.
        """
        Calculate the road height at a specific simulation time.

        Args:
            time_value: Time in seconds.

        Returns:
            float: Road height in meters at the requested time.
        """
        if time_value < self.ramp_time:
            return self.ramp_height * (time_value / self.ramp_time)
        return self.ramp_height
#endregion


#region view
class CarView:
    """Handle the GUI display, schematic, and plot."""

    def __init__(self, args):
        # Chat GPT helped me write this function.
        """
        Create the view from GUI widgets passed in by the main window.

        Args:
            args: Input widgets and display widgets from the GUI.

        Returns:
            None.
        """
        self.input_widgets, self.display_widgets = args

        (
            self.le_m1,
            self.le_v,
            self.le_k1,
            self.le_c1,
            self.le_m2,
            self.le_k2,
            self.le_ang,
            self.le_tmax,
            self.check_include_accel,
        ) = self.input_widgets

        (
            self.gv_schematic,
            self.check_log_x,
            self.check_log_y,
            self.check_log_accel,
            self.check_show_accel,
            self.label_max_min_info,
            self.layout_horizontal_main,
        ) = self.display_widgets

        self._build_tabbed_plots()
        self.build_scene()

    def _build_tabbed_plots(self):
        # Chat GPT helped me write this function.
        """
        Build the tab widget that separates position and force graphs.

        Args:
            None.

        Returns:
            None.
        """
        self.plot_tabs = qtw.QTabWidget()
        self.position_tab = qtw.QWidget()
        self.force_tab = qtw.QWidget()

        self.position_tab_layout = qtw.QVBoxLayout(self.position_tab)
        self.force_tab_layout = qtw.QVBoxLayout(self.force_tab)

        self.position_figure = Figure(tight_layout=True, frameon=True, facecolor="none")
        self.position_canvas = FigureCanvasQTAgg(self.position_figure)
        self.position_toolbar = NavigationToolbar2QT(self.position_canvas, self.position_tab)
        self.position_tab_layout.addWidget(self.position_toolbar)
        self.position_tab_layout.addWidget(self.position_canvas)

        self.force_figure = Figure(tight_layout=True, frameon=True, facecolor="none")
        self.force_canvas = FigureCanvasQTAgg(self.force_figure)
        self.force_toolbar = NavigationToolbar2QT(self.force_canvas, self.force_tab)
        self.force_tab_layout.addWidget(self.force_toolbar)
        self.force_tab_layout.addWidget(self.force_canvas)

        self.position_ax = self.position_figure.add_subplot()
        self.position_accel_ax = self.position_ax.twinx()
        self.force_ax = self.force_figure.add_subplot()

        self.plot_tabs.addTab(self.position_tab, "Position vs. time")
        self.plot_tabs.addTab(self.force_tab, "Force vs time")
        self.layout_horizontal_main.addWidget(self.plot_tabs)

    def update_view(self, model):
        # Chat GPT helped me write this function.
        """
        Update GUI fields and labels from the current model values.

        Args:
            model: CarModel containing the latest inputs and results.

        Returns:
            None.
        """
        self.le_m1.setText(f"{model.m1:0.2f}")
        self.le_k1.setText(f"{model.k1:0.2f}")
        self.le_c1.setText(f"{model.c1:0.2f}")
        self.le_m2.setText(f"{model.m2:0.2f}")
        self.le_k2.setText(f"{model.k2:0.2f}")
        self.le_ang.setText(f"{model.ramp_angle_degrees:0.2f}")
        self.le_tmax.setText(f"{model.tmax:0.2f}")

        summary = (
            f"k1_min = {model.min_k1:0.2f}, k1_max = {model.max_k1:0.2f}\n"
            f"k2_min = {model.min_k2:0.2f}, k2_max = {model.max_k2:0.2f}\n"
            f"SSE = {model.sum_square_error:0.2f}"
        )
        self.label_max_min_info.setText(summary)
        self.plot_results(model)

    def build_scene(self):
        # Chat GPT helped me write this function.
        """
        Build the quarter-car schematic in the graphics view.

        Args:
            None.

        Returns:
            None.
        """
        self.scene = qtw.QGraphicsScene()
        self.scene.setObjectName("QuarterCarSchematic")
        self.scene.setSceneRect(-200, -200, 400, 400)
        self.gv_schematic.setScene(self.scene)

        self.setup_pens_and_brushes()

        self.wheel = Wheel(
            0,
            50,
            50,
            pen=self.pen_wheel,
            wheel_brush=self.brush_wheel,
            mass_brush=self.brush_mass,
            name="Wheel",
        )
        self.car_body = MassBlock(
            0,
            -70,
            100,
            30,
            pen=self.pen_wheel,
            brush=self.brush_mass,
            name="Car Body",
            mass=150,
        )

        self.wheel.add_to_scene(self.scene)
        self.scene.addItem(self.car_body)

        # Road and ramp under the wheel.
        self.scene.addLine(-180, 115, -80, 115, self.pen_road)
        self.scene.addLine(-80, 115, 80, 75, self.pen_road)
        self.scene.addLine(80, 75, 180, 75, self.pen_road)

        # Suspension spring between car body and wheel.
        spring_path = qtg.QPainterPath()
        spring_path.moveTo(-25, -55)
        for point_x, point_y in [
            (-25, -45),
            (-45, -35),
            (-5, -25),
            (-45, -15),
            (-5, -5),
            (-25, 10),
        ]:
            spring_path.lineTo(point_x, point_y)
        self.scene.addPath(spring_path, self.pen_spring)

        # Shock absorber beside the spring.
        self.scene.addLine(25, -55, 25, -25, self.pen_damper)
        self.scene.addRect(15, -25, 20, 30, self.pen_damper)
        self.scene.addLine(25, 5, 25, 20, self.pen_damper)

        body_label = self.scene.addText("m1")
        body_label.setPos(55, -90)
        wheel_label = self.scene.addText("m2")
        wheel_label.setPos(55, 35)

    def setup_pens_and_brushes(self):
        # Chat GPT helped me write this function.
        """
        Create reusable pens and brushes for the schematic.

        Args:
            None.

        Returns:
            None.
        """
        self.pen_wheel = qtg.QPen(qtg.QColor("orange"))
        self.pen_wheel.setWidth(2)

        self.pen_road = qtg.QPen(qtg.QColor("darkGreen"))
        self.pen_road.setWidth(3)

        self.pen_spring = qtg.QPen(qtg.QColor("steelblue"))
        self.pen_spring.setWidth(2)

        self.pen_damper = qtg.QPen(qtg.QColor("dimgray"))
        self.pen_damper.setWidth(2)

        self.brush_wheel = qtg.QBrush(qtg.QColor.fromHsv(35, 255, 255, 64))
        self.brush_mass = qtg.QBrush(qtg.QColor(200, 200, 200, 128))

    def plot_results(self, model):
        # Chat GPT helped me write this function.
        """
        Redraw both the position graph and force graph.

        Args:
            model: CarModel containing calculated time history data.

        Returns:
            None.
        """
        if model.results is None:
            return

        self.plot_position_results(model)
        self.plot_force_results(model)

    def plot_position_results(self, model):
        # Chat GPT helped me write this function.
        """
        Plot body position, wheel position, and optional acceleration.

        Args:
            model: CarModel containing calculated position and acceleration data.

        Returns:
            None.
        """
        ax = self.position_ax
        ax1 = self.position_accel_ax
        ax.clear()
        ax1.clear()

        time_data = model.time_data
        body_position = model.results[:, 0]
        wheel_position = model.results[:, 2]
        acceleration = model.acceleration

        y_values = np.concatenate((body_position, wheel_position, [model.ramp_height]))
        y_min = float(np.min(y_values))
        y_max = float(np.max(y_values))
        y_padding = max((y_max - y_min) * 0.05, 0.001)

        ax.set_xlim(0.001, model.tmax) if self.check_log_x.isChecked() else ax.set_xlim(0.0, model.tmax)
        ax.set_xscale("log" if self.check_log_x.isChecked() else "linear")

        use_log_y = self.check_log_y.isChecked() and np.all(y_values > 0.0)
        if use_log_y:
            ax.set_ylim(max(float(np.min(y_values)) * 0.5, 0.0001), y_max + y_padding)
            ax.set_yscale("log")
        else:
            ax.set_ylim(y_min - y_padding, y_max + y_padding)
            ax.set_yscale("linear")

        ax.plot(time_data, body_position, "b-", label="Body Position")
        ax.plot(time_data, wheel_position, "r-", label="Wheel Position")

        if self.check_show_accel.isChecked() and acceleration is not None:
            ax1.plot(time_data, acceleration, "g-", label="Body Accel")
            ax1.axhline(y=model.max_acceleration, color="orange")

            use_log_accel = self.check_log_accel.isChecked() and np.all(acceleration > 0.0)
            ax1.set_yscale("log" if use_log_accel else "linear")

        ax.set_ylabel("Vertical Position (m)", fontsize="large")
        ax.set_xlabel("time (s)", fontsize="large")
        ax1.set_ylabel("Y'' (g)", fontsize="large")

        ax.axvline(x=model.ramp_time)
        ax.axhline(y=model.ramp_height)
        ax.tick_params(axis="both", which="both", direction="in", top=True, labelsize="large")
        ax1.tick_params(axis="both", which="both", direction="in", right=True, labelsize="large")

        ax.legend()
        self.position_canvas.draw_idle()

    def plot_force_results(self, model):
        # Chat GPT helped me write this function.
        """
        Plot spring and dashpot force values versus time.

        Args:
            model: CarModel containing calculated force data.

        Returns:
            None.
        """
        if model.suspension_spring_force is None:
            return

        ax = self.force_ax
        ax.clear()

        ax.plot(
            model.time_data,
            model.suspension_spring_force,
            "b-",
            label="Suspension spring force, k1",
        )
        ax.plot(model.time_data, model.dashpot_force, "g-", label="Dashpot force, c1")
        ax.plot(model.time_data, model.tire_spring_force, "r-", label="Tire spring force, k2")

        ax.axhline(y=0.0, color="black", linewidth=0.8)
        ax.set_xlim(0.001, model.tmax) if self.check_log_x.isChecked() else ax.set_xlim(0.0, model.tmax)
        ax.set_xscale("log" if self.check_log_x.isChecked() else "linear")

        # Force values can be positive or negative, so symlog is safer than plain log.
        if self.check_log_y.isChecked():
            ax.set_yscale("symlog", linthresh=1.0)
        else:
            ax.set_yscale("linear")

        ax.set_xlabel("time (s)", fontsize="large")
        ax.set_ylabel("Force (N)", fontsize="large")
        ax.set_title("Spring and Dashpot Forces")
        ax.tick_params(axis="both", which="both", direction="in", top=True, labelsize="large")
        ax.legend()
        self.force_canvas.draw_idle()
#endregion


#region controller
class CarController:
    """Coordinate the model calculations and view updates."""

    def __init__(self, args=None):
        # Chat GPT helped me write this function.
        """
        Create the controller and optional GUI view.

        Args:
            args: Optional input and display widgets from the GUI.

        Returns:
            None.
        """
        self.model = CarModel()
        self.view = None
        self.input_widgets = None
        self.display_widgets = None
        self.check_include_accel = None

        if args is not None:
            self.input_widgets, self.display_widgets = args
            (
                self.le_m1,
                self.le_v,
                self.le_k1,
                self.le_c1,
                self.le_m2,
                self.le_k2,
                self.le_ang,
                self.le_tmax,
                self.check_include_accel,
            ) = self.input_widgets
            self.view = CarView(args)

    def _read_float(self, line_edit, label, minimum=None, allow_equal=False):
        # Chat GPT helped me write this function.
        """
        Read and validate a floating-point value from a GUI line edit.

        Args:
            line_edit: QLineEdit containing the user-entered value.
            label: Human-readable name used in error messages.
            minimum: Optional lower limit for the value.
            allow_equal: Whether the value may equal the lower limit.

        Returns:
            float: Validated numeric value from the line edit.
        """
        try:
            value = float(line_edit.text())
        except ValueError as error:
            raise ValueError(f"{label} must be a number.") from error

        if minimum is not None:
            too_small = value < minimum if allow_equal else value <= minimum
            if too_small:
                comparison = "at least" if allow_equal else "greater than"
                raise ValueError(f"{label} must be {comparison} {minimum}.")

        return value

    def _read_gui_inputs(self):
        # Chat GPT helped me write this function.
        """
        Copy user-entered GUI values into the model.

        Args:
            None.

        Returns:
            None.
        """
        if self.view is None:
            return

        self.model.m1 = self._read_float(self.le_m1, "Car body mass", 0.0)
        self.model.m2 = self._read_float(self.le_m2, "Wheel mass", 0.0)
        self.model.c1 = self._read_float(self.le_c1, "Shock absorber damping", 0.0, allow_equal=True)
        self.model.k1 = self._read_float(self.le_k1, "Suspension spring constant", 0.0)
        self.model.k2 = self._read_float(self.le_k2, "Tire spring constant", 0.0)
        self.model.v = self._read_float(self.le_v, "Car speed", 0.0)
        self.model.ramp_angle_degrees = self._read_float(self.le_ang, "Ramp angle", 0.0)
        self.model.tmax = self._read_float(self.le_tmax, "Maximum plot time", 0.0)
        self.model.ramp_height = RAMP_HEIGHT_METERS
        self.model.update_limits()

    def ode_system(self, state, time_value):
        # Chat GPT helped me write this function.
        """
        Calculate the state derivatives for the quarter-car system.

        Args:
            state: Current state vector [x1, x1dot, x2, x2dot].
            time_value: Current simulation time in seconds.

        Returns:
            list: Derivatives [x1dot, x1ddot, x2dot, x2ddot].
        """
        road_height = self.model.road_height_at_time(time_value)

        body_position = state[0]
        body_velocity = state[1]
        wheel_position = state[2]
        wheel_velocity = state[3]

        spring_force = self.model.k1 * (body_position - wheel_position)
        damping_force = self.model.c1 * (body_velocity - wheel_velocity)
        tire_force = self.model.k2 * (wheel_position - road_height)

        # Newton's second law for the sprung and unsprung masses.
        body_acceleration = (-spring_force - damping_force) / self.model.m1
        wheel_acceleration = (spring_force + damping_force - tire_force) / self.model.m2

        return [body_velocity, body_acceleration, wheel_velocity, wheel_acceleration]

    def calculate(self, do_calc=True, print_summary=True):
        # Chat GPT helped me write this function.
        """
        Read inputs, solve the model, update the GUI, and print labeled results.

        Args:
            do_calc: Whether to solve the differential equation.
            print_summary: Whether to print a labeled result summary.

        Returns:
            bool: True when calculation succeeds, otherwise False.
        """
        try:
            self._read_gui_inputs()
            if do_calc:
                self.calculate_sse((self.model.k1, self.model.c1, self.model.k2), optimizing=False)

            if self.view is not None and do_calc:
                self.view.update_view(self.model)
            if print_summary:
                self.print_results("Quarter Car Calculation Results")
            return True
        except ValueError as error:
            self._show_error(str(error))
            return False

    def do_calc(self, do_plot=True, do_accel=True):
        # Chat GPT helped me write this function.
        """
        Solve the quarter-car differential equations.

        Args:
            do_plot: Whether to update the GUI plot after solving.
            do_accel: Whether to calculate body acceleration after solving.

        Returns:
            None.
        """
        speed_mps = 1000.0 * self.model.v / 3600.0
        self.model.ramp_angle_radians = math.radians(self.model.ramp_angle_degrees)
        ramp_sine = math.sin(self.model.ramp_angle_radians)

        if speed_mps <= 0.0 or ramp_sine <= 0.0:
            raise ValueError("Car speed and ramp angle must create a positive ramp time.")

        self.model.ramp_time = self.model.ramp_height / (ramp_sine * speed_mps)
        self.model.time_data = np.linspace(0.0, self.model.tmax, SAMPLE_COUNT)

        initial_conditions = [0.0, 0.0, 0.0, 0.0]
        self.model.results = odeint(self.ode_system, initial_conditions, self.model.time_data)
        self.calculate_forces()

        if do_accel:
            self.calculate_acceleration()
        if do_plot:
            self.plot_results()

    def calculate_acceleration(self):
        # Chat GPT helped me write this function.
        """
        Calculate vertical body acceleration in units of g.

        Args:
            None.

        Returns:
            bool: True when acceleration is calculated.
        """
        body_velocity = self.model.results[:, 1]
        self.model.acceleration = np.gradient(body_velocity, self.model.time_data) / GRAVITY
        self.model.max_acceleration = float(np.max(np.abs(self.model.acceleration)))
        return True

    def calculate_forces(self):
        # Chat GPT helped me write this function.
        """
        Calculate spring and dashpot forces for every time step.

        Args:
            None.

        Returns:
            bool: True when force arrays are calculated.
        """
        body_position = self.model.results[:, 0]
        body_velocity = self.model.results[:, 1]
        wheel_position = self.model.results[:, 2]
        wheel_velocity = self.model.results[:, 3]
        road_position = np.array(
            [self.model.road_height_at_time(time_value) for time_value in self.model.time_data]
        )

        # Use the same sign convention as the differential equations.
        self.model.suspension_spring_force = self.model.k1 * (body_position - wheel_position)
        self.model.dashpot_force = self.model.c1 * (body_velocity - wheel_velocity)
        self.model.tire_spring_force = self.model.k2 * (wheel_position - road_position)

        self.model.max_suspension_spring_force = float(
            np.max(np.abs(self.model.suspension_spring_force))
        )
        self.model.max_dashpot_force = float(np.max(np.abs(self.model.dashpot_force)))
        self.model.max_tire_spring_force = float(np.max(np.abs(self.model.tire_spring_force)))
        return True

    def optimize_suspension(self):
        # Chat GPT helped me write this function.
        """
        Optimize k1, c1, and k2 to reduce road-following error.

        Args:
            None.

        Returns:
            OptimizeResult or None: SciPy result when optimization succeeds.
        """
        if not self.calculate(do_calc=False, print_summary=False):
            return None

        initial_guess = np.array([self.model.k1, self.model.c1, self.model.k2], dtype=float)
        answer = minimize(
            self.calculate_sse,
            initial_guess,
            method="Nelder-Mead",
            options={"maxiter": 300, "xatol": 0.01, "fatol": 0.01},
        )

        self.model.k1, self.model.c1, self.model.k2 = answer.x
        self.calculate_sse(answer.x, optimizing=False)

        if self.view is not None:
            self.view.update_view(self.model)
        self.print_results("Optimized Quarter Car Results")
        return answer

    def calculate_sse(self, values, optimizing=True):
        # Chat GPT helped me write this function.
        """
        Calculate the sum of squared errors for body position versus road height.

        Args:
            values: Iterable containing k1, c1, and k2 values.
            optimizing: Whether to apply optimization penalty terms.

        Returns:
            float: Sum of squared error value.
        """
        k1, c1, k2 = values
        if k1 <= 0.0 or c1 < 0.0 or k2 <= 0.0:
            return LARGE_PENALTY

        self.model.k1 = float(k1)
        self.model.c1 = float(c1)
        self.model.k2 = float(k2)

        try:
            self.do_calc(do_plot=False)
        except ValueError:
            return LARGE_PENALTY

        body_position = self.model.results[:, 0]
        target_position = np.array(
            [self.model.road_height_at_time(time_value) for time_value in self.model.time_data]
        )
        sse = float(np.sum((body_position - target_position) ** 2))

        if optimizing:
            if not self.model.min_k1 <= k1 <= self.model.max_k1:
                sse += OPTIMIZATION_PENALTY
            if c1 < MIN_DAMPING:
                sse += OPTIMIZATION_PENALTY
            if not self.model.min_k2 <= k2 <= self.model.max_k2:
                sse += OPTIMIZATION_PENALTY

            include_acceleration = (
                self.check_include_accel is not None
                and self.check_include_accel.isChecked()
            )
            if include_acceleration and self.model.max_acceleration > self.model.acceleration_limit:
                sse += (self.model.max_acceleration - self.model.acceleration_limit) ** 2

        self.model.sum_square_error = sse
        return sse

    def plot_results(self):
        # Chat GPT helped me write this function.
        """
        Ask the view to redraw the latest model results.

        Args:
            None.

        Returns:
            None.
        """
        if self.view is not None:
            self.view.plot_results(self.model)
        elif self.model.results is not None:
            plt.figure("Position vs. time")
            plt.plot(self.model.time_data, self.model.results[:, 0], label="Body Position")
            plt.plot(self.model.time_data, self.model.results[:, 2], label="Wheel Position")
            plt.xlabel("time (s)")
            plt.ylabel("Vertical Position (m)")
            plt.legend()

            plt.figure("Force vs time")
            plt.plot(
                self.model.time_data,
                self.model.suspension_spring_force,
                label="Suspension spring force, k1",
            )
            plt.plot(self.model.time_data, self.model.dashpot_force, label="Dashpot force, c1")
            plt.plot(self.model.time_data, self.model.tire_spring_force, label="Tire spring force, k2")
            plt.xlabel("time (s)")
            plt.ylabel("Force (N)")
            plt.legend()
            plt.show()

    def print_results(self, title):
        # Chat GPT helped me write this function.
        """
        Print labeled model results for clear grading output.

        Args:
            title: Heading printed above the result values.

        Returns:
            None.
        """
        print(f"\n{title}")
        print("-" * len(title))
        print(f"Car body mass, m1 (kg): {self.model.m1:0.3f}")
        print(f"Wheel mass, m2 (kg): {self.model.m2:0.3f}")
        print(f"Suspension spring, k1 (N/m): {self.model.k1:0.3f}")
        print(f"Shock absorber, c1 (N*s/m): {self.model.c1:0.3f}")
        print(f"Tire spring, k2 (N/m): {self.model.k2:0.3f}")
        print(f"Car speed (kph): {self.model.v:0.3f}")
        print(f"Ramp angle (deg): {self.model.ramp_angle_degrees:0.3f}")
        print(f"Ramp traversal time (s): {self.model.ramp_time:0.5f}")
        print(f"Maximum body acceleration (g): {self.model.max_acceleration:0.5f}")
        print(
            "Maximum suspension spring force, k1 (N): "
            f"{self.model.max_suspension_spring_force:0.5f}"
        )
        print(f"Maximum dashpot force, c1 (N): {self.model.max_dashpot_force:0.5f}")
        print(f"Maximum tire spring force, k2 (N): {self.model.max_tire_spring_force:0.5f}")
        print(f"Sum of squared error: {self.model.sum_square_error:0.5f}")

    def _show_error(self, message):
        # Chat GPT helped me write this function.
        """
        Show and print a clear validation error message.

        Args:
            message: Error text to show to the user.

        Returns:
            None.
        """
        print(f"Input Error: {message}")
        if self.view is not None:
            qtw.QMessageBox.warning(None, "Input Error", message)
#endregion


#region standalone runner
def main():
    # Chat GPT helped me write this function.
    """
    Run the model once with default values for command-line grading checks.

    Args:
        None.

    Returns:
        None.
    """
    controller = CarController()
    controller.calculate(print_summary=True)


if __name__ == "__main__":
    main()
#endregion
