# PyWIB

<p align="center">
  <img src="docs/source/_static/images/logo-pywib.svg" alt="Interaction Lab logo" width="120">
</p>

[![PyPi version](https://badgen.net/pypi/v/pywib/)](https://pypi.org/project/pywib)
[![Latest release](https://badgen.net/github/release/uniovi-hci/pywib)](https://github.com/uniovi-hci/pywib/releases)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![made-with-sphinx-doc](https://img.shields.io/badge/Made%20with-Sphinx-1f425f.svg)](https://www.sphinx-doc.org/)

PyWIB (Python Web Interaction Behaviour) is a Python library for analysing user
interaction data recorded from web pages (mouse movement, clicks, keystrokes,
scrolls) and computing HCI research metrics from it: velocity, acceleration,
jerkiness, angle, trajectory deviations, AUC, click slip, typing speed, pauses,
and more. It also provides trace visualisation and video generation of sessions.

## How to

To install PyWIB, please use:

```bash
pip install pywib
```

### Understand PyWIB

To first understand how to use PyWIB, we suggest taking a look at the [Introduction section](https://uniovi-hci.github.io/pywib/introduction.html) of our documentation, which explains it's main features, limitations and provides a small tutorial on how to start working.

### Prepare your data

PyWIB expects a strucuted input that complies with the following format:

| Column | `ColumnNames` | Meaning |
|---|---|---|
| `sessionId` | `SESSION_ID` | Identifies one user session |
| `eventType` | `EVENT_TYPE` | Integer code, see `EventTypes` |
| `timeStamp` | `TIME_STAMP` | Event time <!-- VERIFY: unit (ms?) and whether absolute or relative --> |
| `x`, `y` | `X`, `Y` | Pointer coordinates <!-- VERIFY: unit (CSS pixels?) and origin --> |
| `elementId` | `ELEMENT_ID` | Target element |
| `sceneId` | `SCENE_ID` | Page or scene identifier |
| `keyValue`, `keyCode` | `KEY_VALUE`, `KEY_CODE` | Keyboard events |

This data structure is further explained in the [documentation](https://uniovi-hci.github.io/pywib/data_structure.html).

### Process user data

A minimal example of how to use PyWIB is presented here. If you require deeper information about the librarys API please consult the [documentation](https://uniovi-hci.github.io/pywib/).

```python
from pywib import to_pywib_df, velocity, velocity_metrics, visualize_trace, ColumnNames

# Considering an already loaded CSV into a pandas DataFrame

df = to_pywib_df(df, "sessionIdCol", "xCoordinateCol", "yCoordinateCol", "timeStampCol", "eventTypeCol", "keyValueCol", "keyCodeCol").copy()

v = velocity(df, per_traces=True)
v_metrics = velocity_metrics(df=None, traces=v)

userSession = df[df[ColumnNames.SESSION_ID] == "USER_A"].copy()
visualize_trace(userSession, userSession.index, "USER_A", type="info", save_path="user_a_trace.png")
```

## Running the tests
First, navigate to the PyWIB folder
```bash
cd pywib
```

Then install the required dependencies using python, use a virtual environment if you wish to.
```python
pip install pytest
pip install -r requirements.txt
```
Then, run the tests using:
```python
pytest test
```

## Citation

If you use our tool in your research, we kindly ask you to cite us.

G. D. Carvajal-Aza, A. Alvarez-Varela, J. De Andres, M. Gonzalez-Rodriguez, D. Fernandez-Lanvin, and M. Paino, "PyWIB: A Python Library for a Multi-Modal Approach to Web Interaction Behavior Analysis," in *Proceedings of the 2026 IARIA Annual Congress on Frontiers in Science, Technology, Services, and Applications (IARIA Congress 2026)*, Nice, France, Jul. 2026, pp. 103–108. Available: https://www.thinkmind.org/library/IARIA_CONGRESS/IARIA_Congress_2026/iaria_congress_2026_1_170_50103.html


## Generating Documentation

For bulding the PyWIB documentation in your local device, use:

```
cd pywib/docs
make html
```

And then access `docs/build/html/index.html` to navigate.