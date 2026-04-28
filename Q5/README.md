# Q5 Quarter Car Model

This program updates the quarter car GUI to show two graphs in a tab widget:

- Position vs. time
- Force vs. time

The force graph displays:

- Suspension spring force, k1
- Dashpot force, c1
- Tire spring force, k2

## Files to Upload

- `Car_app.py`
- `Car_GUI.py`
- `Car_GUI.ui`
- `QuarterCarModel.py`
- `requirements.txt`
- `README.md`

## How to Run

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the GUI:

```bash
python Car_app.py
```

The Calculate button updates both tabs. The first tab shows position results, and the second tab shows spring and dashpot force results.
