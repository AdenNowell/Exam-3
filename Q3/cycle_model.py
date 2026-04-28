#region imports
from dataclasses import dataclass, field

from air_properties import Air, PlotData
#endregion


#region data classes
@dataclass
class CycleInputs:
    """
    Stores the user inputs after conversion to SI units.

    Args:
        cycle_type: Cycle name, using otto, diesel, or dual.
        temperature_1: State 1 temperature in K.
        pressure_1: State 1 pressure in Pa.
        volume_1: Total cylinder volume at bottom dead center in m^3.
        compression_ratio: Compression ratio V1/V2.
        temperature_high: Otto cycle high temperature in K.
        cutoff_ratio: Diesel or dual cycle cutoff ratio.
        pressure_ratio: Dual cycle pressure ratio P3/P2.

    Returns:
        A single container for validated cycle inputs.
    """

    cycle_type: str
    temperature_1: float
    pressure_1: float
    volume_1: float
    compression_ratio: float
    temperature_high: float = 1800.0
    cutoff_ratio: float = 2.0
    pressure_ratio: float = 1.5


@dataclass
class CycleResults:
    """
    Stores calculated air-standard cycle results in SI molar units.

    Args:
        cycle_type: Cycle name, using otto, diesel, or dual.
        states: Ordered list of calculated StatePoint objects.
        processes: Ordered list of PlotData objects for process curves.
        moles: Amount of air in the cylinder in mol.
        heat_added: Molar heat input in J/mol.
        heat_rejected: Molar heat rejection in J/mol.
        compression_work: Molar compression work input in J/mol.
        power_work: Molar expansion or power-stroke work output in J/mol.
        net_work: Molar cycle net work output in J/mol.
        efficiency: Thermal efficiency in percent.

    Returns:
        A complete cycle-result container for the controller and view.
    """

    cycle_type: str
    states: list = field(default_factory=list)
    processes: list = field(default_factory=list)
    moles: float = 0.0
    heat_added: float = 0.0
    heat_rejected: float = 0.0
    compression_work: float = 0.0
    power_work: float = 0.0
    net_work: float = 0.0
    efficiency: float = 0.0
#endregion


#region model
class AirStandardCycleModel:
    """
    Calculates Otto, Diesel, and Dual air-standard cycles.

    Args:
        None.

    Returns:
        A model object that stores the latest calculated results.
    """

    # Chat GPT helped me write this function.
    def __init__(self):
        """
        Initializes the model and its working-fluid calculator.

        Args:
            None.

        Returns:
            None.
        """
        self.air = Air()
        self.results = None

    # Chat GPT helped me write this function.
    def calculate(self, inputs):
        """
        Calculates the selected thermodynamic cycle.

        Args:
            inputs: CycleInputs object with all values in SI units.

        Returns:
            CycleResults object containing states, process curves, and performance values.
        """
        self._validate_common_inputs(inputs)
        cycle_type = inputs.cycle_type.lower().strip()

        if cycle_type == "otto":
            self.results = self._calculate_otto(inputs)
        elif cycle_type == "diesel":
            self.results = self._calculate_diesel(inputs)
        elif cycle_type == "dual":
            self.results = self._calculate_dual(inputs)
        else:
            raise ValueError("Cycle type must be Otto, Diesel, or Dual.")

        return self.results

    # Chat GPT helped me write this function.
    def _calculate_otto(self, inputs):
        """
        Calculates the four-state air-standard Otto cycle.

        Args:
            inputs: CycleInputs object with an Otto high temperature.

        Returns:
            CycleResults object for the Otto cycle.
        """
        if inputs.temperature_high <= inputs.temperature_1:
            raise ValueError("Otto high temperature must be greater than the initial temperature.")

        state_1 = self.air.set(pressure=inputs.pressure_1, temperature=inputs.temperature_1, name="State 1 - BDC")
        moles = inputs.volume_1 / state_1.specific_volume
        state_2 = self.air.set(specific_volume=state_1.specific_volume / inputs.compression_ratio, entropy=state_1.entropy, name="State 2 - TDC")
        state_3 = self.air.set(temperature=inputs.temperature_high, specific_volume=state_2.specific_volume, name="State 3 - TDC")
        state_4 = self.air.set(specific_volume=state_1.specific_volume, entropy=state_3.entropy, name="State 4 - BDC")

        heat_added = state_3.internal_energy - state_2.internal_energy
        heat_rejected = state_4.internal_energy - state_1.internal_energy
        compression_work = state_2.internal_energy - state_1.internal_energy
        power_work = state_3.internal_energy - state_4.internal_energy

        states = [state_1, state_2, state_3, state_4]
        processes = [
            self._sample_isentropic_process(state_1, state_2, "1-2 Isentropic Compression"),
            self._sample_constant_volume_process(state_2, state_3, "2-3 Constant Volume Heat Addition"),
            self._sample_isentropic_process(state_3, state_4, "3-4 Isentropic Expansion"),
            self._sample_constant_volume_process(state_4, state_1, "4-1 Constant Volume Heat Rejection"),
        ]
        return self._build_results("Otto", states, processes, moles, heat_added, heat_rejected, compression_work, power_work)

    # Chat GPT helped me write this function.
    def _calculate_diesel(self, inputs):
        """
        Calculates the four-state air-standard Diesel cycle.

        Args:
            inputs: CycleInputs object with a Diesel cutoff ratio.

        Returns:
            CycleResults object for the Diesel cycle.
        """
        if inputs.cutoff_ratio <= 1.0:
            raise ValueError("Diesel cutoff ratio must be greater than 1.")
        if inputs.cutoff_ratio >= inputs.compression_ratio:
            raise ValueError("Diesel cutoff ratio must be less than the compression ratio.")

        state_1 = self.air.set(pressure=inputs.pressure_1, temperature=inputs.temperature_1, name="State 1 - BDC")
        moles = inputs.volume_1 / state_1.specific_volume
        state_2 = self.air.set(specific_volume=state_1.specific_volume / inputs.compression_ratio, entropy=state_1.entropy, name="State 2 - TDC")
        state_3 = self.air.set(pressure=state_2.pressure, specific_volume=state_2.specific_volume * inputs.cutoff_ratio, name="State 3 - Cutoff")
        state_4 = self.air.set(specific_volume=state_1.specific_volume, entropy=state_3.entropy, name="State 4 - BDC")

        heat_added = state_3.enthalpy - state_2.enthalpy
        heat_rejected = state_4.internal_energy - state_1.internal_energy
        compression_work = state_2.internal_energy - state_1.internal_energy
        constant_pressure_work = state_2.pressure * (state_3.specific_volume - state_2.specific_volume)
        expansion_work = state_3.internal_energy - state_4.internal_energy
        power_work = constant_pressure_work + expansion_work

        states = [state_1, state_2, state_3, state_4]
        processes = [
            self._sample_isentropic_process(state_1, state_2, "1-2 Isentropic Compression"),
            self._sample_constant_pressure_process(state_2, state_3, "2-3 Constant Pressure Heat Addition"),
            self._sample_isentropic_process(state_3, state_4, "3-4 Isentropic Expansion"),
            self._sample_constant_volume_process(state_4, state_1, "4-1 Constant Volume Heat Rejection"),
        ]
        return self._build_results("Diesel", states, processes, moles, heat_added, heat_rejected, compression_work, power_work)

    # Chat GPT helped me write this function.
    def _calculate_dual(self, inputs):
        """
        Calculates the five-state air-standard Dual cycle.

        Args:
            inputs: CycleInputs object with pressure and cutoff ratios.

        Returns:
            CycleResults object for the Dual cycle.
        """
        if inputs.pressure_ratio <= 1.0:
            raise ValueError("Dual pressure ratio P3/P2 must be greater than 1.")
        if inputs.cutoff_ratio <= 1.0:
            raise ValueError("Dual cutoff ratio must be greater than 1.")
        if inputs.cutoff_ratio >= inputs.compression_ratio:
            raise ValueError("Dual cutoff ratio must be less than the compression ratio.")

        state_1 = self.air.set(pressure=inputs.pressure_1, temperature=inputs.temperature_1, name="State 1 - BDC")
        moles = inputs.volume_1 / state_1.specific_volume
        state_2 = self.air.set(specific_volume=state_1.specific_volume / inputs.compression_ratio, entropy=state_1.entropy, name="State 2 - TDC")
        state_3 = self.air.set(pressure=state_2.pressure * inputs.pressure_ratio, specific_volume=state_2.specific_volume, name="State 3 - Constant Volume End")
        state_4 = self.air.set(pressure=state_3.pressure, specific_volume=state_3.specific_volume * inputs.cutoff_ratio, name="State 4 - Cutoff")
        state_5 = self.air.set(specific_volume=state_1.specific_volume, entropy=state_4.entropy, name="State 5 - BDC")

        heat_added = (state_3.internal_energy - state_2.internal_energy) + (state_4.enthalpy - state_3.enthalpy)
        heat_rejected = state_5.internal_energy - state_1.internal_energy
        compression_work = state_2.internal_energy - state_1.internal_energy
        constant_pressure_work = state_3.pressure * (state_4.specific_volume - state_3.specific_volume)
        expansion_work = state_4.internal_energy - state_5.internal_energy
        power_work = constant_pressure_work + expansion_work

        states = [state_1, state_2, state_3, state_4, state_5]
        processes = [
            self._sample_isentropic_process(state_1, state_2, "1-2 Isentropic Compression"),
            self._sample_constant_volume_process(state_2, state_3, "2-3 Constant Volume Heat Addition"),
            self._sample_constant_pressure_process(state_3, state_4, "3-4 Constant Pressure Heat Addition"),
            self._sample_isentropic_process(state_4, state_5, "4-5 Isentropic Expansion"),
            self._sample_constant_volume_process(state_5, state_1, "5-1 Constant Volume Heat Rejection"),
        ]
        return self._build_results("Dual", states, processes, moles, heat_added, heat_rejected, compression_work, power_work)

    # Chat GPT helped me write this function.
    def _build_results(self, cycle_type, states, processes, moles, heat_added, heat_rejected, compression_work, power_work):
        """
        Creates a CycleResults object from common cycle quantities.

        Args:
            cycle_type: Display name of the cycle.
            states: Ordered list of StatePoint objects.
            processes: Ordered list of PlotData objects.
            moles: Amount of air in the cylinder in mol.
            heat_added: Molar heat input in J/mol.
            heat_rejected: Molar heat rejection in J/mol.
            compression_work: Molar compression work input in J/mol.
            power_work: Molar power-stroke work output in J/mol.

        Returns:
            CycleResults object with net work and efficiency included.
        """
        net_work = power_work - compression_work
        efficiency = 100.0 * net_work / heat_added
        return CycleResults(
            cycle_type=cycle_type,
            states=states,
            processes=processes,
            moles=moles,
            heat_added=heat_added,
            heat_rejected=heat_rejected,
            compression_work=compression_work,
            power_work=power_work,
            net_work=net_work,
            efficiency=efficiency,
        )

    # Chat GPT helped me write this function.
    def _sample_isentropic_process(self, start_state, end_state, name, point_count=40):
        """
        Samples an isentropic process for plotting.

        Args:
            start_state: Starting StatePoint.
            end_state: Ending StatePoint.
            name: Curve label.
            point_count: Number of plotted states.

        Returns:
            PlotData object containing states along the isentropic curve.
        """
        process = PlotData(name=name)
        for specific_volume in self._linspace(start_state.specific_volume, end_state.specific_volume, point_count):
            process.add_state(self.air.set(specific_volume=specific_volume, entropy=start_state.entropy, name=name))
        return process

    # Chat GPT helped me write this function.
    def _sample_constant_volume_process(self, start_state, end_state, name, point_count=40):
        """
        Samples a constant-volume process for plotting.

        Args:
            start_state: Starting StatePoint.
            end_state: Ending StatePoint.
            name: Curve label.
            point_count: Number of plotted states.

        Returns:
            PlotData object containing states along the constant-volume curve.
        """
        process = PlotData(name=name)
        for temperature in self._linspace(start_state.temperature, end_state.temperature, point_count):
            process.add_state(self.air.set(temperature=temperature, specific_volume=start_state.specific_volume, name=name))
        return process

    # Chat GPT helped me write this function.
    def _sample_constant_pressure_process(self, start_state, end_state, name, point_count=40):
        """
        Samples a constant-pressure process for plotting.

        Args:
            start_state: Starting StatePoint.
            end_state: Ending StatePoint.
            name: Curve label.
            point_count: Number of plotted states.

        Returns:
            PlotData object containing states along the constant-pressure curve.
        """
        process = PlotData(name=name)
        for temperature in self._linspace(start_state.temperature, end_state.temperature, point_count):
            process.add_state(self.air.set(temperature=temperature, pressure=start_state.pressure, name=name))
        return process

    # Chat GPT helped me write this function.
    def _validate_common_inputs(self, inputs):
        """
        Validates the inputs shared by all cycles.

        Args:
            inputs: CycleInputs object to check.

        Returns:
            None.
        """
        if inputs.temperature_1 <= 0.0:
            raise ValueError("Initial temperature must be greater than zero.")
        if inputs.pressure_1 <= 0.0:
            raise ValueError("Initial pressure must be greater than zero.")
        if inputs.volume_1 <= 0.0:
            raise ValueError("Cylinder volume must be greater than zero.")
        if inputs.compression_ratio <= 1.0:
            raise ValueError("Compression ratio must be greater than 1.")

    # Chat GPT helped me write this function.
    def _linspace(self, start, end, point_count):
        """
        Creates evenly spaced values without requiring NumPy.

        Args:
            start: First value in the sequence.
            end: Last value in the sequence.
            point_count: Number of points to create.

        Returns:
            A list of evenly spaced values from start to end.
        """
        if point_count <= 1:
            return [start]
        step = (end - start) / (point_count - 1)
        return [start + index * step for index in range(point_count)]
#endregion
