Dependent Metrics and Cases that affect them
============================================

Window Resizing and Zooming
-------------------------

Changing the size of a window and zooming in and out of the screen alter its resolution. 
This causes metrics related to movement and trajectory to become less effective, as the coordinates taken from the user movement are not directly proportional to the actual movement he is describinig.

For this reason, normalization is required to maintain the correct proportions of distance.

Mobile VS Computer
------------------

Mobile users tend to perform a wider range of "movements" than computer users, as touchscreens allow a higher degree of freedom when interacting with them than traditional keyboards or computer mice.


Keyboard differences
~~~~~~~~~~~~~~~~~~~~~
Keyboard metrics in mobile devices must be taken with caution, as users may type while dragging their finger across the keyboard, causing events of type "Key down" to be lees frequent while events of type "Key up" are generated.




