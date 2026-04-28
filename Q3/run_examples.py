#region imports
from cycle_model import AirStandardCycleModel, CycleInputs
#endregion


#region helpers
# Chat GPT helped me write this function.
def total_kj(molar_energy, moles):
    """
    Converts molar energy to total energy in kJ.

    Args:
        molar_energy: Energy per mole in J/mol.
        moles: Amount of air in mol.

    Returns:
        Total energy in kJ.
    """
    return molar_energy * moles / 1000.0


# Chat GPT helped me write this function.
def print_cycle_results(title, results):
    """
    Prints one labeled cycle summary for the TA.

    Args:
        title: Heading text for the cycle case.
        results: CycleResults object to print.

    Returns:
        None.
    """
    print("=" * 72)
    print(title)
    print("=" * 72)
    print("State Results:")
    for index, state in enumerate(results.states, start=1):
        print(
            f"  State {index}: "
            f"T = {state.temperature:10.3f} K, "
            f"P = {state.pressure / 1000.0:10.3f} kPa, "
            f"v = {state.specific_volume:10.6f} m^3/mol"
        )
    print("Cycle Performance:")
    print(f"  Heat Added       = {total_kj(results.heat_added, results.moles):10.4f} kJ")
    print(f"  Heat Rejected    = {total_kj(results.heat_rejected, results.moles):10.4f} kJ")
    print(f"  Compression Work = {total_kj(results.compression_work, results.moles):10.4f} kJ")
    print(f"  Power Work       = {total_kj(results.power_work, results.moles):10.4f} kJ")
    print(f"  Net Work         = {total_kj(results.net_work, results.moles):10.4f} kJ")
    print(f"  Efficiency       = {results.efficiency:10.3f} %")
    print()


# Chat GPT helped me write this function.
def main():
    """
    Runs Part A and Part B example calculations.

    Args:
        None.

    Returns:
        None.
    """
    model = AirStandardCycleModel()
    volume_1 = 0.003

    otto_inputs = CycleInputs(
        cycle_type="otto",
        temperature_1=300.0,
        pressure_1=100000.0,
        volume_1=volume_1,
        compression_ratio=8.0,
        temperature_high=1800.0,
    )
    diesel_inputs = CycleInputs(
        cycle_type="diesel",
        temperature_1=300.0,
        pressure_1=100000.0,
        volume_1=volume_1,
        compression_ratio=18.0,
        cutoff_ratio=2.0,
    )
    dual_inputs = CycleInputs(
        cycle_type="dual",
        temperature_1=300.0,
        pressure_1=100000.0,
        volume_1=volume_1,
        compression_ratio=18.0,
        pressure_ratio=1.5,
        cutoff_ratio=1.2,
    )

    print("Assumed V1 = 0.003 m^3 for total work and heat values.")
    print_cycle_results("Part A - Otto Cycle Example", model.calculate(otto_inputs))
    print_cycle_results("Part A - Diesel Cycle Example", model.calculate(diesel_inputs))
    print_cycle_results("Part B - Dual Cycle Example", model.calculate(dual_inputs))


if __name__ == "__main__":
    main()
#endregion
