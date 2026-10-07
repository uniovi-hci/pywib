Jerkiness
=========
.. autofunction:: pywib.jerkiness

.. role:: python(code)
   :language: python


Practical Example
--------------------
.. code-block:: python

    from pywib import jerkiness
    jk_df = jerkiness(data_df, per_traces=True)

    for _, traces in jk_df.items():
        for trace in traces:
            print(trace[['time', 'x', 'y', 'jerkiness']].head())
   
Notes
------
The method can be either run with either :python:`per_traces=True` or :python:`per_traces=False`, the first one segments the data by movement traces, while the second one computes the jerkiness for the entire DataFrame.

This is important to consider for the specific given dataset, if the data contains **anything else than movement data**, then :python:`per_traces=True` should be used to avoid incorrect jerkiness calculations. Whereas a dataset of consecutive movement events can be processed with `per_traces=False` to obtain a single jerkiness DataFrame.

Jerkiness Metrics
=================
.. autofunction:: pywib.jerkiness_metrics

Practical Example
--------------------
.. code-block:: python
    
    from pywib import jerkiness_metrics
    metrics = jerkiness_metrics(data_df)

    for session, session in metrics.items():
        print(f"Session: {session}, Mean Jerkiness: {session['mean']}, Max Jerkiness: {session['max']}, Min Jerkiness: {session['min']}")