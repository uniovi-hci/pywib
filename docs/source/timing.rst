Timing Metrics
=================

This section covers metrics related to time, mainly those that quantify the duration of user interactions during sessions.

.. currentmodule:: pywib

Execution Time
--------------
This metric can also be referred to as "Total time" or "Session time", as it represents the overall duration of a user session from the first recorded event to the last. 
It can be useful when filtering sessions based on their length if the task being studied has a defined expected minimum duration.
It is important to note that this metric does not account for periods of inactivity or pauses within the session.

Function :py:func:`~pywib.execution_time` computes the total execution time for each session by calculating the difference between the maximum and minimum timestamps within that session.

Movement Time
--------------
This metric focuses on the active movement periods during a session, excluding any idle times, and provides a more accurate representation of the time spent in motion by the user.
It is mainly useful when focusing on the time of the actual interaction, rather than for filtering based on total session duration.

Function :py:func:`~pywib.movement_time` calculates the total movement time for each session by summing the time intervals between consecutive interaction points where movement occurs.

Number of pauses
----------------
Function :py:func:`~pywib.num_pauses` computes the number of pauses by each session, giving as a result.
This function maintains the principle of having two separate behaviours depending on the segmentation.
If the DataFrame is not segmented by traces, then all events are taken into account to compute pauses, even clicks, scrolls, keystrokes, etc.
But if the DataFrame is segmented, then it will only computed pauses given during the times of movement. 
This is crucial to understand what our data represents, as we may want to consider those pauses that happen right after a click or a key press instead of only those given at movement time.

The metrics for this pauses can be obtained using the method :py:func:`~pywib.pauses_metrics`, which will return a dictorionary with the sessionId as keys and the following metrics:
- total_pauses
- mean_pause_duration
- pause_durations
- max_pause
- min_pause
