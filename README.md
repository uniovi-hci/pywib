# PyWIB

Pywib (Python Web Interaction Behaviour) is a library desgined for analysing and obtaning metrics from users interaction with web pages.

## How to
```python
from pywib import velocity, velocity_metrics
v = velocity(df_all_sessions)
v_metrics = velocity_metrics(None, v)
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
```
cd pywib/docs
make html
```