Keystorke Dynamics
==================


.. role:: python(code)
   :language: python

.. TODO add durations

Typing Speed
-------------

.. autofunction:: pywib.typing_speed
Practical Example
~~~~~~~~~~~~~~~~~
.. code-block:: python

   from pywib import typing_speed

    speed = typing_speed(data_frame)

    for session_id, speed_value in speed.items():
        print(f"Session ID: {session_id}")
        print(f"Typing Speed (CPM): {speed_value}")

Notes
~~~~~
CPM stands for Characters Per Minute, and it is calculated by taking the total number of keystrokes (characters typed) and dividing it by the total time taken (in minutes) to type those characters.

The method can be either run with either :python:`per_traces=True` or :python:`per_traces=False`, the first one segments the data by groups of keystroke events, while the second one computes the speed for the entire DataFrame without pauses into consideration.

This is important to consider for the specific given dataset, if the data contains anything else than keystroke data, then :python:`per_traces=True` should be used to avoid incorrect CPM calculations. Whereas a dataset of consecutive keystroke events can be processed with per_traces=False to obtain a single CPM.

Backspace Usage
-----------------
.. autofunction:: pywib.backspace_usage

Practical Example
~~~~~~~~~~~~~~~~~

.. code-block:: python
    
    from pywib import backspace_usage
    
     backspace_counts = backspace_usage(data_frame)
    
     for session_id, count in backspace_counts.items():
          print(f"Session ID: {session_id}")
          print(f"Backspace Usage: {count}")