# Air Standard Cycle MVC Solution

This folder contains a clean MVC solution for the Otto, Diesel, and Dual air-standard cycles.

## Files

- `air_properties.py`: ideal-gas air property calculations with variable specific heats.
- `cycle_model.py`: model layer for Otto, Diesel, and Dual cycle calculations.
- `OttoDieselDual_app.py`: PyQt5 GUI, view, and controller.
- `OttoDiesel_app.py`: small launcher wrapper for the GUI.
- `run_examples.py`: prints labeled Part A and Part B example results.

## Run the GUI

```powershell
python OttoDieselDual_app.py
```

The wrapper also works:

```powershell
python OttoDiesel_app.py
```

## Run the Printed Examples

```powershell
python run_examples.py
```

## Input Units

SI mode uses K, kPa, and m^3. English mode uses R, atm, and ft^3.

For the Diesel example in the prompt, enter:

- T1 = 300 K
- P1 = 100 kPa
- compression ratio = 18
- cutoff ratio = 2

For the Dual example in the prompt, enter:

- T1 = 300 K
- P1 = 100 kPa
- compression ratio = 18
- pressure ratio P3/P2 = 1.5
- cutoff ratio = 1.2
