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


Keyboard Interaction in Touch Devices vs Desktop Devices
-------------------------------------------------------

When a user types by sliding a finger across a virtual keyboard without
lifting it from the screen, the finger's path is not captured by the web
page. Virtual keyboards such as Gboard, SwiftKey, and the iOS keyboard are
separate applications rendered over the browser. Touches on the keyboard
therefore do not generate pointer or touch events in the page, so the
sliding path is not available to the tracking script.

The page usually receives the completed word as text through composition and
``input`` events. The exact keyboard events depend on the operating system,
keyboard, and browser:

* On Android with Chrome or Samsung Internet, Gboard generally uses
  composition mode, including when letters are entered one at a time.
  Keyboard events commonly report ``key="Unidentified"`` with key code 229,
  often as a ``keydown``/``keyup`` pair for each change to the word being
  composed rather than one event per letter.
* On iPhone with Safari, individual taps may produce the actual letters in
  keyboard events. With QuickPath (swipe typing), however, the word is
  usually inserted as a single text change and keyboard events may not be
  generated.

Consequently, with the current agent, a word entered by swiping may produce
only some ``keydown``/``keyup`` events with ``Unidentified`` on Android, no
keyboard events on iPhone, or neither the entered text nor the finger's path.
The path itself is not recoverable from these events.

To record swipe-typed text, the tracking script should listen for ``input``
and, optionally, ``compositionend`` events and store the inserted text and
the type of insertion as a dedicated event. This would allow the log to
represent an interaction such as “the word *hello* was inserted”, while still
not providing the finger's route across the keyboard.



Mobile VS Computer
------------------

Mobile users tend to perform a wider range of "movements" than computer users, as touchscreens allow a higher degree of freedom when interacting with them than traditional keyboards or computer mice.


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