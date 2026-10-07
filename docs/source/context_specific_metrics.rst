Context Specific Metrics
========================

Metrics that are valid for analyzing mouse movements in a desktop web application may not be valid for analyzing touch interactions on mobile devices.
Therefore, it is crucial to consider the context in which the metrics will be applied and to validate them accordingly.

Moreover, the setup of an experiment itself can influence the validity of certain metrics :cite:p:`Schoemann2019-vv,Kuric2024-wc`, which is why **PyWIB** encourages users to validate the metrics they compute in their specific context and experiment setup.

Mouse Clicks and Touch Taps
---------------------------
On a touchscreen, a single tap generates both Pointer events:

====================  ===  =   ===========  
eventType             x    y   timeStamp    
====================  ===  =   ===========  
EVENT_POINTER_DOWN    0    0   100   
EVENT_POINTER_UP      0    0   200     
EVENT_POINTER_MOVE    200  0   300 
====================  ===  =   ===========  

And Mouse events that directly replicate the touch interaction afterwards:

====================  ===  =   ===========  
eventType             x    y   timeStamp    
====================  ===  =   ===========  
EVENT_ON_MOUSE_DOWN   0    0   100   
EVENT_ON_MOUSE_UP     0    0   200 
EVENT_ON_CLICK        0    0   200 
EVENT_ON_MOUSE_MOVE   200  0   300 
====================  ===  =   ===========  

.. important::
    This also applies to double taps, which generate the same sequence of events twice, with the second tap generating a `EVENT_ON_DOUBLE_CLICK` event at the end of the sequence.

For the same interaction. Browsers always dispatch this fixed sequence of compatibility mouse events after touch input, for backwards compatibility.

Check if your tracking script supports this case and if it is of your interest to remove or keep this events, otherwise filtering has to happen during data preparation, since **PyWIB does not manage this case**.

Reference: https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener


Keyboard ineraction in Touch devices vs Desktop devices
--------------------------------------------------------

Window Scrolling and Zooming
-----------------------------

Total Distance
--------------

Consider a session with 5 events, if event number 3 is not a movement event (i.e: click, keyboard), then computing its total distance gives a smaller value when computing it by traces than by the whole DataFrame.
The following table illustrates a case in which a user performs a click event on timeStamp 300 and causes the total computed distance to be less than the expected total (400).


==================  =========  ===  =   ===  ==  ===========  ========
Trace               eventType  x    y   dx   dy  timeStamp    distance
==================  =========  ===  =   ===  ==  ===========  ========
Trace 1             0          0    0   0    0   100          0
Trace 1             0          100  0   100  0   200          100
**Trace boundary**  3          200  0   0    0   300          _
Trace 2             0          300  0   100  0   200          100
Trace 2             0          400  0   100  0   200          100
==================  =========  ===  =   ===  ==  ===========  ========