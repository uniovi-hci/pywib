Angle
========
.. autofunction:: pywib.angle

.. role:: python(code)
   :language: python

Practical Example
-----------------
.. code-block:: python

   from pywib import angle

    # Calculate the angle
    df_angle = angle(df, per_traces=True)
    
    # Iterate over traces to obtain angle values
    for session_id, traces in df_angle.items():
        print(f"Session ID: {session_id}")
        for trace in traces:
            print(f"Velocity values:\n{trace['angle']}")
                
Notes
------
The method can be either run with either :python:`per_traces=True` or :python:`per_traces=False`, the first one segments the data by movement traces, while the second one computes the velocity for the entire DataFrame.

Angular Velocity
================

.. autofunction:: pywib.angular_velocity

Practical Example
-----------------
.. code-block:: python

   from pywib import angular_velocity

    angular_v = angular_velocity(data_frame, per_traces=True)

    for session_id, traces in angular_v.items():
        print(f"Session ID: {session_id}")
        for trace in traces:
            print(f"Velocity values:\n{trace['angular_velocity']}")

Angular Acceleration
====================

.. autofunction:: pywib.angular_acceleration

Practical Example
-----------------
.. code-block:: python

   from pywib import angular_acceleration

    angular_v = angular_acceleration(data_frame, per_traces=True)

    for session_id, traces in angular_v.items():
        print(f"Session ID: {session_id}")
        for trace in traces:
            print(f"Velocity values:\n{trace['angular_acceleration']}")