Mouse Metrics
=================

.. currentmodule:: pywib

.. note::
    On a touchscreen, a single tap generates both Pointer events (EVENT_POINTER_DOWN/MOVE/UP/CANCEL) and Mouse events (EVENT_ON_MOUSE_DOWN/MOVE/UP, EVENT_ON_CLICK/DOUBLE_CLICK) for the same interaction. Browsers always dispatch this fixed sequence of compatibility mouse events after touch input, for backwards compatibility.
    
    Check if your tracking script supports this case, otherwise filtering has to happen during data analysis. 
    
    Reference: https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListeners

Number of Clicks
-----------------

This metric counts the total number of clicks recorded during a session. See the function implementation in :py:func:`~pywib.number_of_clicks`.

Click Slip
----------

This metric measures the deviation of click positions from the intended targets, providing insights into user accuracy. As such, the click slip is computed as the distance between an :py:const:`EVENT_ON_MOUSE_DOWN` and an :py:const:`EVENT_ON_MOUSE_UP`.
See the function implementation in :py:func:`~pywib.click_slip`.

