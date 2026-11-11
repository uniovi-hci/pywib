Acceleration
============

.. autofunction:: pywib.acceleration

.. role:: python(code)
   :language: python


Practical Example
-----------------
.. code-block:: python

    from pywib import acceleration, velocity, compute_space_time_diff
    df = compute_space_time_diff(df_data)
    acceleration_traces = acceleration(None, velocity(df, per_traces=True), per_traces=True)
    for _, traces in acceleration_traces.items():
        for trace in traces:
            print(trace['acceleration'])

Notes
------
The method can be either run with either :python:`per_traces=True` or :python:`per_traces=False`, the first one segments the data by movement traces, while the second one computes the acceleration for the entire DataFrame.

This is important to consider for the specific given dataset, if the data contains **anything else than movement data**, then :python:`per_traces=True` should be used to avoid incorrect acceleration calculations. Whereas a dataset of consecutive movement events can be processed with `per_traces=False` to obtain a single acceleration DataFrame.

Acceleration Metrics
====================

.. autofunction:: pywib.acceleration_metrics

Practical Example
-----------------
.. code-block:: python
    
    from pywib import acceleration_metrics
    acc_metrics = acceleration_metrics(data_df)

    for _, session in acc_metrics.items():
        print(f"Session Acceleration Metrics:")
        print(f" Mean Acceleration: {session['mean']}")
        print(f" Max Acceleration: {session['max']}")
        print(f" Min Acceleration: {session['min']}")