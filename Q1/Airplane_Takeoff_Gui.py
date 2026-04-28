#region Imports
import math
import tkinter as tk
from tkinter import messagebox, ttk

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ModuleNotFoundError:
    FigureCanvasTkAgg = None
    Figure = None
#endregion


#region Constants
DEFAULT_WEIGHT = 56000.0
DEFAULT_THRUST = 13000.0
WING_AREA = 1000.0
MAX_LIFT_COEFFICIENT = 2.4
DRAG_COEFFICIENT = 0.0279
AIR_DENSITY = 0.002377
GRAVITY_CONSTANT = 32.174
WEIGHT_OFFSET = 10000.0
MINIMUM_THRUST = 3000.0
MAXIMUM_THRUST = 30000.0
THRUST_POINTS = 100
#endregion


#region Model
class TakeoffDistanceModel:
    """Model that calculates airplane takeoff distance values."""

    # Chat GPT helped me write this function.
    def calculate_stall_velocity(self, weight):
        """
        Calculate the stall velocity for a given airplane weight.

        Args:
            weight: Airplane weight in pounds.

        Returns:
            Stall velocity as a float.
        """
        lift_denominator = (
            0.5 * AIR_DENSITY * WING_AREA * MAX_LIFT_COEFFICIENT
        )
        return math.sqrt(weight / lift_denominator)

    # Chat GPT helped me write this function.
    def calculate_takeoff_velocity(self, weight):
        """
        Calculate the takeoff velocity from the stall velocity.

        Args:
            weight: Airplane weight in pounds.

        Returns:
            Takeoff velocity as a float.
        """
        stall_velocity = self.calculate_stall_velocity(weight)
        return 1.2 * stall_velocity

    # Chat GPT helped me write this function.
    def calculate_acceleration_factor(self, weight, thrust):
        """
        Calculate the acceleration factor A from thrust and weight.

        Args:
            weight: Airplane weight in pounds.
            thrust: Engine thrust in pounds.

        Returns:
            Acceleration factor as a float.
        """
        return GRAVITY_CONSTANT * (thrust / weight)

    # Chat GPT helped me write this function.
    def calculate_drag_factor(self, weight):
        """
        Calculate the drag factor B for a given airplane weight.

        Args:
            weight: Airplane weight in pounds.

        Returns:
            Drag factor as a float.
        """
        drag_force_factor = 0.5 * AIR_DENSITY * WING_AREA * DRAG_COEFFICIENT
        return (GRAVITY_CONSTANT / weight) * drag_force_factor

    # Chat GPT helped me write this function.
    def calculate_takeoff_distance(self, weight, thrust):
        """
        Calculate takeoff distance using the assignment equations.

        Args:
            weight: Airplane weight in pounds.
            thrust: Engine thrust in pounds.

        Returns:
            Takeoff distance as a float.
        """
        takeoff_velocity = self.calculate_takeoff_velocity(weight)
        acceleration_factor = self.calculate_acceleration_factor(weight, thrust)
        drag_factor = self.calculate_drag_factor(weight)

        # The logarithm form evaluates the required integral exactly.
        denominator_at_takeoff = (
            acceleration_factor - drag_factor * takeoff_velocity ** 2
        )

        if denominator_at_takeoff <= 0:
            raise ValueError(
                "Thrust is too low for the airplane to reach takeoff speed."
            )

        return (
            -1.0
            / (2.0 * drag_factor)
            * math.log(denominator_at_takeoff / acceleration_factor)
        )

    # Chat GPT helped me write this function.
    def create_thrust_values(self, selected_thrust):
        """
        Create thrust values for drawing smooth graph lines.

        Args:
            selected_thrust: User-entered thrust value in pounds.

        Returns:
            List of thrust values as floats.
        """
        upper_thrust = max(MAXIMUM_THRUST, selected_thrust * 1.25)
        thrust_step = (upper_thrust - MINIMUM_THRUST) / (THRUST_POINTS - 1)
        return [
            MINIMUM_THRUST + thrust_step * point_number
            for point_number in range(THRUST_POINTS)
        ]

    # Chat GPT helped me write this function.
    def create_graph_data(self, weight, thrust):
        """
        Create all takeoff-distance data needed for the graph.

        Args:
            weight: User-entered airplane weight in pounds.
            thrust: User-entered engine thrust in pounds.

        Returns:
            Dictionary containing thrust values, curve data, and selected point.
        """
        thrust_values = self.create_thrust_values(thrust)
        curve_weights = [weight - WEIGHT_OFFSET, weight, weight + WEIGHT_OFFSET]
        curves = []

        for curve_weight in curve_weights:
            if curve_weight <= 0:
                continue

            # Each curve keeps the same weight while thrust changes.
            distance_values = [
                self.calculate_takeoff_distance(curve_weight, thrust_value)
                for thrust_value in thrust_values
            ]
            curves.append((curve_weight, distance_values))

        selected_distance = self.calculate_takeoff_distance(weight, thrust)

        return {
            "thrust_values": thrust_values,
            "curves": curves,
            "selected_point": (thrust, selected_distance),
        }
#endregion


#region View
class TakeoffDistanceView:
    """View that displays the GUI and matplotlib graph."""

    # Chat GPT helped me write this function.
    def __init__(self, root):
        """
        Build the GUI widgets and graph area.

        Args:
            root: Main tkinter window for the program.

        Returns:
            None.
        """
        if Figure is None or FigureCanvasTkAgg is None:
            raise ModuleNotFoundError(
                "matplotlib is required for this GUI. "
                "Install it with: pip install matplotlib"
            )

        self.root = root
        self.root.title("Airplane Takeoff Distance")
        self.root.geometry("900x650")

        self.input_frame = ttk.Frame(self.root, padding=12)
        self.graph_frame = ttk.Frame(self.root, padding=(12, 0, 12, 12))

        self.weight_entry = ttk.Entry(self.input_frame, width=18)
        self.thrust_entry = ttk.Entry(self.input_frame, width=18)
        self.calculate_button = ttk.Button(self.input_frame, text="Calculate")
        self.output_label = ttk.Label(self.root, text="")

        self.figure = Figure(figsize=(7, 4.8), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)

        self.create_layout()

    # Chat GPT helped me write this function.
    def create_layout(self):
        """
        Place labels, entries, button, output text, and graph on the window.

        Args:
            None.

        Returns:
            None.
        """
        self.input_frame.pack(fill=tk.X)
        self.input_frame.columnconfigure(1, weight=1)
        self.input_frame.columnconfigure(3, weight=1)

        ttk.Label(self.input_frame, text="Weight (lb):").grid(
            row=0, column=0, padx=6, pady=6, sticky=tk.W
        )
        self.weight_entry.grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(self.input_frame, text="Thrust (lb):").grid(
            row=0, column=2, padx=6, pady=6, sticky=tk.W
        )
        self.thrust_entry.grid(row=0, column=3, padx=6, pady=6)

        self.calculate_button.grid(row=0, column=4, padx=10, pady=6)
        self.output_label.pack(fill=tk.X, padx=18, pady=(0, 8))
        self.graph_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Chat GPT helped me write this function.
    def set_default_inputs(self, weight, thrust):
        """
        Display default weight and thrust values in the entry boxes.

        Args:
            weight: Default airplane weight in pounds.
            thrust: Default engine thrust in pounds.

        Returns:
            None.
        """
        self.weight_entry.insert(0, f"{weight:.0f}")
        self.thrust_entry.insert(0, f"{thrust:.0f}")

    # Chat GPT helped me write this function.
    def get_inputs(self):
        """
        Read weight and thrust values entered by the user.

        Args:
            None.

        Returns:
            Tuple containing weight and thrust as floats.
        """
        weight = float(self.weight_entry.get())
        thrust = float(self.thrust_entry.get())
        return weight, thrust

    # Chat GPT helped me write this function.
    def set_calculate_command(self, command):
        """
        Connect the calculate button to a controller command.

        Args:
            command: Function to run when the calculate button is clicked.

        Returns:
            None.
        """
        self.calculate_button.config(command=command)

    # Chat GPT helped me write this function.
    def show_error(self, message):
        """
        Show an error message to the user.

        Args:
            message: Explanation of what went wrong.

        Returns:
            None.
        """
        messagebox.showerror("Input Error", message)

    # Chat GPT helped me write this function.
    def update_output(self, weight, thrust, distance):
        """
        Display a clear text result below the input controls.

        Args:
            weight: Airplane weight in pounds.
            thrust: Engine thrust in pounds.
            distance: Takeoff distance in feet.

        Returns:
            None.
        """
        self.output_label.config(
            text=(
                f"Selected Weight: {weight:,.0f} lb | "
                f"Selected Thrust: {thrust:,.0f} lb | "
                f"Takeoff Distance: {distance:,.2f} ft"
            )
        )

    # Chat GPT helped me write this function.
    def draw_graph(self, graph_data):
        """
        Draw the takeoff-distance graph on the GUI.

        Args:
            graph_data: Dictionary containing thrust values, curves, and point.

        Returns:
            None.
        """
        self.axes.clear()
        thrust_values = graph_data["thrust_values"]

        for curve_weight, distance_values in graph_data["curves"]:
            self.axes.plot(
                thrust_values,
                distance_values,
                label=f"Weight = {curve_weight:,.0f} lb",
            )

        selected_thrust, selected_distance = graph_data["selected_point"]
        self.axes.plot(
            selected_thrust,
            selected_distance,
            marker="o",
            markersize=9,
            markerfacecolor="none",
            markeredgecolor="black",
            linestyle="none",
            label="Selected value",
        )

        self.axes.set_title("Takeoff Distance vs. Thrust")
        self.axes.set_xlabel("Thrust (lb)")
        self.axes.set_ylabel("Takeoff Distance, S_TO (ft)")
        self.axes.grid(True)
        self.axes.legend()
        self.figure.tight_layout()
        self.canvas.draw()
#endregion


#region Controller
class TakeoffDistanceController:
    """Controller that connects user actions to model calculations."""

    # Chat GPT helped me write this function.
    def __init__(self, model, view):
        """
        Store the model and view, then connect the calculate button.

        Args:
            model: TakeoffDistanceModel object for calculations.
            view: TakeoffDistanceView object for display.

        Returns:
            None.
        """
        self.model = model
        self.view = view
        self.view.set_calculate_command(self.calculate_and_display)

    # Chat GPT helped me write this function.
    def calculate_and_display(self):
        """
        Validate inputs, calculate distances, and update the display.

        Args:
            None.

        Returns:
            None.
        """
        try:
            weight, thrust = self.view.get_inputs()
            self.validate_inputs(weight, thrust)
            graph_data = self.model.create_graph_data(weight, thrust)
            selected_distance = graph_data["selected_point"][1]

            self.view.update_output(weight, thrust, selected_distance)
            self.view.draw_graph(graph_data)
            self.print_results(weight, thrust, selected_distance)
        except ValueError as error:
            self.view.show_error(str(error))

    # Chat GPT helped me write this function.
    def validate_inputs(self, weight, thrust):
        """
        Make sure the user entered positive numeric values.

        Args:
            weight: Airplane weight entered by the user.
            thrust: Engine thrust entered by the user.

        Returns:
            None.
        """
        if weight <= 0:
            raise ValueError("Weight must be greater than zero.")

        if thrust <= 0:
            raise ValueError("Thrust must be greater than zero.")

    # Chat GPT helped me write this function.
    def print_results(self, weight, thrust, distance):
        """
        Print a clearly labeled result for the grader.

        Args:
            weight: Airplane weight in pounds.
            thrust: Engine thrust in pounds.
            distance: Takeoff distance in feet.

        Returns:
            None.
        """
        print("Airplane Takeoff Distance Result")
        print(f"Weight: {weight:,.0f} lb")
        print(f"Thrust: {thrust:,.0f} lb")
        print(f"Takeoff Distance: {distance:,.2f} ft")
        print("-" * 40)
#endregion


#region Program Start
# Chat GPT helped me write this function.
def main():
    """
    Start the takeoff-distance GUI program.

    Args:
        None.

    Returns:
        None.
    """
    root = tk.Tk()
    model = TakeoffDistanceModel()
    view = TakeoffDistanceView(root)
    TakeoffDistanceController(model, view)

    view.set_default_inputs(DEFAULT_WEIGHT, DEFAULT_THRUST)
    view.calculate_button.invoke()
    root.mainloop()


if __name__ == "__main__":
    main()
#endregion
