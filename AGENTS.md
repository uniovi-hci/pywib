# AGENTS.md

PyWIB (Python Web Interaction Behaviour) is a Python library for analysing user
interaction data recorded from web pages (mouse movement, clicks, keystrokes,
scrolls) and computing HCI research metrics from it: velocity, acceleration,
jerkiness, angle, trajectory deviations, AUC, click slip, typing speed, pauses,
and more. It also provides trace visualisation and video generation of sessions.

- Docs: https://uniovi-hci.github.io/pywib/
- PyPI: https://pypi.org/project/pywib/ (install name `pywib`, import name `pywib`)
- License: Apache-2.0

This file has two parts. Read the one that matches your task:

1. **Using PyWIB** — you are writing code that imports the library.
2. **Developing PyWIB** — you are modifying this repository.

<!-- VERIFY: this file was drafted without access to the mcp-integration branch.
Every item marked VERIFY below must be checked against the current code and docs,
then the marker removed. -->

---

## 1. Using PyWIB

### Install and import

```bash
pip install pywib
```

```python
import pywib                      # the import name is lowercase
from pywib import velocity, velocity_metrics
```

Always import from `pywib` (lowercase). Some older docs examples use `PyWIB`;
that is wrong on case-sensitive filesystems.

### Mental model

PyWIB works on **event logs held in pandas DataFrames**. The typical pipeline is:

1. Load recorded events into a DataFrame (one row per event).
2. Preprocess (compute per-row differences such as `dt`, `dx`, `dy`).
3. Segment events into **traces** (continuous movement or typing episodes).
4. Compute per-event values (e.g. `velocity`) and/or per-session metrics.

A **trace** is one continuous episode of interaction. Most functions return a
dictionary keyed by session ID, whose values are **lists of DataFrames**, one
per trace:

```
dict[str, list[pd.DataFrame]]    # {sessionId: [trace_df, trace_df, ...]}
```

Metric functions (e.g. `velocity_metrics`) return a dictionary keyed by session
ID with summary statistics as values, e.g. `{"s1": {"mean": ..., "max": ..., "min": ...}}`.

### Input data

Check the documentation: https://uniovi-hci.github.io/pywib/data_structure.html

Input DataFrames use these column names (use the `ColumnNames` constants rather
than string literals):

| Column | `ColumnNames` | Meaning |
|---|---|---|
| `sessionId` | `SESSION_ID` | Identifies one user session |
| `eventType` | `EVENT_TYPE` | Integer code, see `EventTypes` |
| `timeStamp` | `TIME_STAMP` | Event time <!-- VERIFY: unit (ms?) and whether absolute or relative --> |
| `x`, `y` | `X`, `Y` | Pointer coordinates <!-- VERIFY: unit (CSS pixels?) and origin --> |
| `elementId` | `ELEMENT_ID` | Target element |
| `sceneId` | `SCENE_ID` | Page or scene identifier |
| `keyValue`, `keyCode` | `KEY_VALUE`, `KEY_CODE` | Keyboard events |

Derived columns created by preprocessing and metrics include `dt`, `dx`, `dy`,
`distance`, `velocity`, `acceleration`, `jerkiness`, `angle`.

Event types are integer codes mapped from JavaScript events, available as
`EventTypes` (for example `EVENT_ON_MOUSE_MOVE = 0`, `EVENT_ON_CLICK = 1`,
`EVENT_KEY_DOWN = 13`, `EVENT_KEY_UP = 15`). Look up codes in the constants
instead of hardcoding numbers.

If a user's data has different column names, rename the columns to the names
above before calling PyWIB. Do not modify the library.

### Rules for writing correct code

1. **Pass arguments by keyword.** Signatures look like
   `velocity(df=None, traces=None, per_traces=True, parallel=False, n_jobs=2)`
   and `velocity_metrics(df=None, traces=None)`. The first positional argument is
   `df`, not `traces`. To compute metrics from the output of `velocity()`, which
   is a traces dictionary, write `velocity_metrics(traces=vel)`.
2. **Respect `per_traces`.** Use `per_traces=True` whenever the DataFrame contains
   anything other than movement events (clicks, keys, scrolls). `per_traces=False`
   is only correct for a DataFrame of consecutive movement events or specific analysis cases. Consider your use case.
3. **Run preprocessing first.** Movement metrics need `dt`, `dx` and `dy`.
   <!-- VERIFY: name and import path of the preprocessing function
   (the docs mention compute_space_time_diff) and whether velocity() computes
   these columns itself -->
4. **Do not invent functions or parameters.** If you are unsure a function exists,
   check the API reference: https://uniovi-hci.github.io/pywib/api/index.html
5. **Treat metrics as context-dependent.** Metrics validated for desktop mouse
   input may not be valid for touch input, and experimental setup affects validity.
   Report results as descriptive measurements, and say so when the data came
   from mobile or touch events. Do not draw psychological, cognitive or
   identity conclusions from the numbers. Check the documentation: https://uniovi-hci.github.io/pywib/context_specific_metrics.html
6. **Large datasets.** Recorded interaction data can reach gigabytes. Prefer
   processing per session.

### Minimal working example

```python
import pandas as pd
from pywib import velocity, velocity_metrics, ColumnNames

df = pd.DataFrame({
    ColumnNames.SESSION_ID: ["s1"] * 5,
    ColumnNames.EVENT_TYPE: [0, 0, 0, 0, 0],            # EventTypes.EVENT_ON_MOUSE_MOVE
    ColumnNames.TIME_STAMP: [0, 10, 20, 30, 40],
    ColumnNames.X: [0, 5, 12, 20, 30],
    ColumnNames.Y: [0, 2, 4, 7, 11],
})

vel = velocity(df, per_traces=True)          # {sessionId: [trace DataFrames]}
metrics = velocity_metrics(traces=vel)       # {sessionId: {"mean", "max", "min"}}
print(metrics["s1"]["mean"])
```

### Where to find things

| Need | Docs page |
|---|---|
| Velocity, acceleration, jerkiness, angle | Movement Metrics |
| Path length, AUC, deviations, direction changes | Trajectory Metrics |
| Click count, click slip | Mouse Metrics |
| Typing duration, speed, backspace usage | Keystroke Metrics |
| Execution time, movement time, pauses | Timing Metrics |
| How events become traces | Segmentation |
| Plots, session video, keystroke heatmap | Visualization |
| Column names and event codes | Constants |

Base URL: https://uniovi-hci.github.io/pywib/ (machine-readable index: `llms.txt`
at the same root).

---

## 2. Developing PyWIB

### Layout

```
src/pywib/    library source
test/         pytest suite
docs/         Sphinx documentation (Furo theme)
pyproject.toml, setup.py, requirements.txt   packaging
```

### Commands

```bash
pip install -r requirements.txt
pip install pytest
pytest test                  # run the tests

pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints sphinxcontrib-bibtex myst-parser furo sphinx-apa-references
cd docs && make html         # build the documentation
```

<!-- VERIFY: Python version support, linter/formatter, and whether the package
should be installed editable (pip install -e .) before running tests -->

### Conventions

- **Metrics are research-validated.** Never change a metric's formula or output
  columns without explicit instruction. Behaviour changes need a docs update and a test.
- **Use `ColumnNames`, `EventTypes` and `ComponentTypes`** from the constants
  module instead of string or integer literals.
- **Every public function needs:** type hints, a docstring describing every
  parameter and the exact return structure, a docs page entry, and a test.
- **Every docs example must run as written**, with all imports and a small
  inline DataFrame. Do not leave undefined helper functions in examples.
- **When the public API changes,** update the docs and `llms.txt` in the same commit.
