Mouse Metrics
=================

.. currentmodule:: pywib

Number of Clicks
-----------------

This metric counts the total number of clicks recorded during a session. See the function implementation in :py:func:`~pywib.number_of_clicks`.

Click Slip
----------

This metric measures the deviation of click positions from the intended targets, providing insights into user accuracy. As such, the click slip is computed as the distance between an :py:const:`EVENT_ON_MOUSE_DOWN` and an :py:const:`EVENT_ON_MOUSE_UP`.
See the function implementation in :py:func:`~pywib.click_slip`.

