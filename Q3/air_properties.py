#region imports
import math
from copy import deepcopy
from dataclasses import dataclass, field
#endregion


#region data classes
@dataclass
class StatePoint:
    """
    Stores the thermodynamic properties for one ideal-gas air state.

    Args:
        name: Short label for the state.
        temperature: Temperature in K.
        pressure: Pressure in Pa.
        internal_energy: Molar internal energy in J/mol.
        enthalpy: Molar enthalpy in J/mol.
        entropy: Molar entropy in J/(mol*K).
        specific_volume: Molar specific volume in m^3/mol.

    Returns:
        A container object with named thermodynamic properties.
    """

    name: str = ""
    temperature: float = 0.0
    pressure: float = 0.0
    internal_energy: float = 0.0
    enthalpy: float = 0.0
    entropy: float = 0.0
    specific_volume: float = 0.0

    # Chat GPT helped me write this function.
    def get_value(self, property_name):
        """
        Returns a property value using the one-letter plot name.

        Args:
            property_name: One of P, T, u, h, s, or v.

        Returns:
            The matching state property in SI molar units.
        """
        property_map = {
            "p": self.pressure,
            "t": self.temperature,
            "u": self.internal_energy,
            "h": self.enthalpy,
            "s": self.entropy,
            "v": self.specific_volume,
        }
        return property_map[property_name.lower()]


@dataclass
class PlotData:
    """
    Stores state points for one plotted process curve.

    Args:
        name: Label for the process curve.
        states: Ordered list of StatePoint objects along the curve.

    Returns:
        A process data container for plotting.
    """

    name: str = ""
    states: list = field(default_factory=list)

    # Chat GPT helped me write this function.
    def add_state(self, state):
        """
        Adds one thermodynamic state to the process curve.

        Args:
            state: StatePoint object to append to the curve.

        Returns:
            None.
        """
        self.states.append(state)

    # Chat GPT helped me write this function.
    def values(self, property_name):
        """
        Gets one property for every state in the process curve.

        Args:
            property_name: One of P, T, u, h, s, or v.

        Returns:
            A list of numeric property values.
        """
        return [state.get_value(property_name) for state in self.states]
#endregion


#region ideal gas air model
class Air:
    """
    Calculates ideal-gas air properties with variable specific heats.

    Args:
        None.

    Returns:
        An ideal-gas air property calculator.
    """

    # Chat GPT helped me write this function.
    def __init__(self):
        """
        Initializes air constants and the reference state.

        Args:
            None.

        Returns:
            None.
        """
        self.r_bar = 8.3145
        self.molecular_weight = 28.97
        self.standard_state = StatePoint(
            name="Reference State",
            temperature=273.15,
            pressure=101325.0,
            internal_energy=0.0,
            enthalpy=0.0,
            entropy=0.0,
            specific_volume=self.r_bar * 273.15 / 101325.0,
        )
        self.state = deepcopy(self.standard_state)

    # Chat GPT helped me write this function.
    def cp(self, temperature):
        """
        Calculates the molar constant-pressure specific heat of air.

        Args:
            temperature: Air temperature in K.

        Returns:
            Molar specific heat cp in J/(mol*K).
        """
        self._require_positive(temperature, "temperature")
        low_temperature_range = 1630.0
        a = 3.653 if temperature < low_temperature_range else 2.753
        b = -1.337e-3 if temperature < low_temperature_range else 0.002
        c = 3.294e-6 if temperature < low_temperature_range else -1.0e-6
        d = -1.913e-9 if temperature < low_temperature_range else 3.0e-10
        e = 0.2763e-12 if temperature < low_temperature_range else -3.0e-14
        return self.r_bar * (a + b * temperature + c * temperature**2 + d * temperature**3 + e * temperature**4)

    # Chat GPT helped me write this function.
    def cv(self, temperature):
        """
        Calculates the molar constant-volume specific heat of air.

        Args:
            temperature: Air temperature in K.

        Returns:
            Molar specific heat cv in J/(mol*K).
        """
        return self.cp(temperature) - self.r_bar

    # Chat GPT helped me write this function.
    def delta_u(self, temperature_1=None, temperature_2=None):
        """
        Calculates a molar internal energy change for ideal-gas air.

        Args:
            temperature_1: Initial temperature in K, using the reference state when None.
            temperature_2: Final temperature in K, using the reference state when None.

        Returns:
            Molar internal energy change in J/mol.
        """
        temperature_1 = self.standard_state.temperature if temperature_1 is None else temperature_1
        temperature_2 = self.standard_state.temperature if temperature_2 is None else temperature_2
        return self._integrate(self.cv, temperature_1, temperature_2)

    # Chat GPT helped me write this function.
    def delta_h(self, temperature_1=None, temperature_2=None):
        """
        Calculates a molar enthalpy change for ideal-gas air.

        Args:
            temperature_1: Initial temperature in K, using the reference state when None.
            temperature_2: Final temperature in K, using the reference state when None.

        Returns:
            Molar enthalpy change in J/mol.
        """
        temperature_1 = self.standard_state.temperature if temperature_1 is None else temperature_1
        temperature_2 = self.standard_state.temperature if temperature_2 is None else temperature_2
        return self._integrate(self.cp, temperature_1, temperature_2)

    # Chat GPT helped me write this function.
    def delta_s_tv(self, temperature_1=None, temperature_2=None, volume_1=None, volume_2=None):
        """
        Calculates a molar entropy change from temperature and volume.

        Args:
            temperature_1: Initial temperature in K, using the reference state when None.
            temperature_2: Final temperature in K, using the reference state when None.
            volume_1: Initial molar specific volume in m^3/mol, using the reference state when None.
            volume_2: Final molar specific volume in m^3/mol, using the reference state when None.

        Returns:
            Molar entropy change in J/(mol*K).
        """
        temperature_1 = self.standard_state.temperature if temperature_1 is None else temperature_1
        temperature_2 = self.standard_state.temperature if temperature_2 is None else temperature_2
        volume_1 = self.standard_state.specific_volume if volume_1 is None else volume_1
        volume_2 = self.standard_state.specific_volume if volume_2 is None else volume_2
        self._require_positive(volume_1, "volume_1")
        self._require_positive(volume_2, "volume_2")

        integrand = lambda temperature: self.cv(temperature) / temperature
        entropy_change = self._integrate(integrand, temperature_1, temperature_2)
        entropy_change += self.r_bar * math.log(volume_2 / volume_1)
        return entropy_change

    # Chat GPT helped me write this function.
    def delta_s_tp(self, temperature_1=None, temperature_2=None, pressure_1=None, pressure_2=None):
        """
        Calculates a molar entropy change from temperature and pressure.

        Args:
            temperature_1: Initial temperature in K, using the reference state when None.
            temperature_2: Final temperature in K, using the reference state when None.
            pressure_1: Initial pressure in Pa, using the reference state when None.
            pressure_2: Final pressure in Pa, using the reference state when None.

        Returns:
            Molar entropy change in J/(mol*K).
        """
        temperature_1 = self.standard_state.temperature if temperature_1 is None else temperature_1
        temperature_2 = self.standard_state.temperature if temperature_2 is None else temperature_2
        pressure_1 = self.standard_state.pressure if pressure_1 is None else pressure_1
        pressure_2 = self.standard_state.pressure if pressure_2 is None else pressure_2
        self._require_positive(pressure_1, "pressure_1")
        self._require_positive(pressure_2, "pressure_2")

        integrand = lambda temperature: self.cp(temperature) / temperature
        entropy_change = self._integrate(integrand, temperature_1, temperature_2)
        entropy_change += self.r_bar * math.log(pressure_1 / pressure_2)
        return entropy_change

    # Chat GPT helped me write this function.
    def set(self, pressure=None, temperature=None, specific_volume=None, enthalpy=None, internal_energy=None, entropy=None, name=""):
        """
        Sets an air state from two independent thermodynamic properties.

        Args:
            pressure: Pressure in Pa.
            temperature: Temperature in K.
            specific_volume: Molar specific volume in m^3/mol.
            enthalpy: Molar enthalpy in J/mol.
            internal_energy: Molar internal energy in J/mol.
            entropy: Molar entropy in J/(mol*K).
            name: Short label for the state.

        Returns:
            A deep copy of the calculated StatePoint.
        """
        known_count = sum(value is not None for value in [pressure, temperature, specific_volume, enthalpy, internal_energy, entropy])
        if known_count != 2:
            raise ValueError("Exactly two independent properties are required to set an air state.")

        if pressure is not None and temperature is not None:
            state = self._state_from_pressure_temperature(pressure, temperature, name)
        elif temperature is not None and specific_volume is not None:
            pressure = self.r_bar * temperature / specific_volume
            state = self._state_from_pressure_temperature(pressure, temperature, name)
        elif pressure is not None and specific_volume is not None:
            temperature = pressure * specific_volume / self.r_bar
            state = self._state_from_pressure_temperature(pressure, temperature, name)
        elif specific_volume is not None and entropy is not None:
            temperature = self._solve_temperature_for_entropy_volume(entropy, specific_volume)
            pressure = self.r_bar * temperature / specific_volume
            state = self._state_from_pressure_temperature(pressure, temperature, name)
        elif pressure is not None and entropy is not None:
            temperature = self._solve_temperature_for_entropy_pressure(entropy, pressure)
            state = self._state_from_pressure_temperature(pressure, temperature, name)
        elif pressure is not None and enthalpy is not None:
            temperature = self._solve_temperature(lambda trial_temperature: self.delta_h(temperature_2=trial_temperature) - enthalpy)
            state = self._state_from_pressure_temperature(pressure, temperature, name)
        elif pressure is not None and internal_energy is not None:
            temperature = self._solve_temperature(lambda trial_temperature: self.delta_u(temperature_2=trial_temperature) - internal_energy)
            state = self._state_from_pressure_temperature(pressure, temperature, name)
        else:
            raise ValueError("The supplied property pair is not supported for ideal-gas air.")

        self.state = state
        return deepcopy(self.state)

    # Chat GPT helped me write this function.
    def _state_from_pressure_temperature(self, pressure, temperature, name):
        """
        Calculates all state properties from pressure and temperature.

        Args:
            pressure: Pressure in Pa.
            temperature: Temperature in K.
            name: Short label for the state.

        Returns:
            A complete StatePoint object.
        """
        self._require_positive(pressure, "pressure")
        self._require_positive(temperature, "temperature")
        specific_volume = self.r_bar * temperature / pressure
        internal_energy = self.delta_u(temperature_2=temperature)
        enthalpy = self.delta_h(temperature_2=temperature)
        entropy = self.delta_s_tp(temperature_2=temperature, pressure_2=pressure)
        return StatePoint(name, temperature, pressure, internal_energy, enthalpy, entropy, specific_volume)

    # Chat GPT helped me write this function.
    def _solve_temperature_for_entropy_volume(self, entropy, specific_volume):
        """
        Solves for temperature from molar entropy and molar specific volume.

        Args:
            entropy: Molar entropy in J/(mol*K).
            specific_volume: Molar specific volume in m^3/mol.

        Returns:
            Temperature in K.
        """
        self._require_positive(specific_volume, "specific_volume")
        residual = lambda trial_temperature: self.delta_s_tv(temperature_2=trial_temperature, volume_2=specific_volume) - entropy
        return self._solve_temperature(residual)

    # Chat GPT helped me write this function.
    def _solve_temperature_for_entropy_pressure(self, entropy, pressure):
        """
        Solves for temperature from molar entropy and pressure.

        Args:
            entropy: Molar entropy in J/(mol*K).
            pressure: Pressure in Pa.

        Returns:
            Temperature in K.
        """
        self._require_positive(pressure, "pressure")
        residual = lambda trial_temperature: self.delta_s_tp(temperature_2=trial_temperature, pressure_2=pressure) - entropy
        return self._solve_temperature(residual)

    # Chat GPT helped me write this function.
    def _solve_temperature(self, residual_function):
        """
        Finds a physically reasonable temperature root for a state equation.

        Args:
            residual_function: Function that returns zero at the desired temperature.

        Returns:
            Temperature in K.
        """
        lower_temperature = 20.0
        upper_temperature = 6000.0
        for unused_index in range(20):
            lower_value = residual_function(lower_temperature)
            upper_value = residual_function(upper_temperature)
            if math.isclose(lower_value, 0.0, abs_tol=1.0e-9):
                return lower_temperature
            if math.isclose(upper_value, 0.0, abs_tol=1.0e-9):
                return upper_temperature
            if lower_value * upper_value < 0.0:
                for unused_bisection_index in range(100):
                    middle_temperature = 0.5 * (lower_temperature + upper_temperature)
                    middle_value = residual_function(middle_temperature)
                    if math.isclose(middle_value, 0.0, abs_tol=1.0e-8):
                        return middle_temperature
                    if lower_value * middle_value < 0.0:
                        upper_temperature = middle_temperature
                        upper_value = middle_value
                    else:
                        lower_temperature = middle_temperature
                        lower_value = middle_value
                return 0.5 * (lower_temperature + upper_temperature)
            lower_temperature = max(1.0, lower_temperature / 2.0)
            upper_temperature *= 1.5
        raise ValueError("Could not solve for a positive air temperature from the supplied properties.")

    # Chat GPT helped me write this function.
    def _integrate(self, function, start, end, interval_count=400):
        """
        Integrates a smooth function using Simpson's rule.

        Args:
            function: Callable function of one variable.
            start: Lower integration limit.
            end: Upper integration limit.
            interval_count: Even number of integration intervals.

        Returns:
            Approximate definite integral value.
        """
        if math.isclose(start, end, abs_tol=1.0e-12):
            return 0.0
        if interval_count % 2 == 1:
            interval_count += 1
        direction = 1.0
        if end < start:
            start, end = end, start
            direction = -1.0

        step = (end - start) / interval_count
        total = function(start) + function(end)
        for index in range(1, interval_count):
            coefficient = 4.0 if index % 2 == 1 else 2.0
            total += coefficient * function(start + index * step)
        return direction * total * step / 3.0

    # Chat GPT helped me write this function.
    def _require_positive(self, value, value_name):
        """
        Validates that a thermodynamic property is positive.

        Args:
            value: Numeric value to validate.
            value_name: Name used in the error message.

        Returns:
            None.
        """
        if value <= 0.0:
            raise ValueError(f"{value_name} must be greater than zero.")
#endregion
