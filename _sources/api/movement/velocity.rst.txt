Velocity
========
.. autofunction:: pywib.velocity

.. role:: python(code)
   :language: python

Practical Example
-----------------
.. code-block:: python

   from pywib import velocity

    df = compute_space_time_diff(data_frame)
    # Calculate velocity
    df_velocity = velocity(df, per_traces=True)
    
    # Iterate over traces to obtain velocity values
    for session_id, traces in df_velocity.items():
        print(f"Session ID: {session_id}")
        for trace in traces:
            print(f"Velocity values:\n{trace['velocity']}")
                
Notes
------
The method can be either run with either :python:`per_traces=True` or :python:`per_traces=False`, the first one segments the data by movement traces, while the second one computes the velocity for the entire DataFrame.

This is important to consider for the specific given dataset, if the data contains **anything else than movement data**, then :python:`per_traces=True` should be used to avoid incorrect velocity calculations. Whereas a dataset of consecutive movement events can be processed with `per_traces=False` to obtain a single velocity DataFrame.


Velocity Metrics
================


.. autofunction:: pywib.velocity_metrics

Practical Example
-----------------
.. code-block:: python

   from pywib import velocity_metrics

    metrics = velocity_metrics(data_frame)

    for _, session_id in metrics.items():
        print(f"Mean Velocity: {session_id['mean']}")
        print(f"Max Velocity: {session_id['max']}")
        print(f"Min Velocity: {session_id['min']}")