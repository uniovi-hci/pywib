Movement Metrics
================

.. currentmodule:: pywib

Velocity
--------

The velocity is the rate of change of position with respect to time. Commonly used to analyze the speed of movement during user interactions :cite:p:`Kieslich2019-mt, Katerina2018-ch`.
Computer mouses have been proven to be reliable enough to measure human velocity :cite:p:`OReilly2011-dw` and have even been considered as valid tools to obtain markers for cognitive immpairment :cite:p:`Seelye2015-yx`.
Velocity and time have also been proven to be affected by aging :cite:p:`Pariente-Martinez2016-te` up to a certain point and for some activies carried out in computers and web enviornments.

The function :py:func:`~pywib.velocity` computes the velocity based on the distance and time difference between consecutive points.
The velocity is calculated as:

.. |xi| replace:: :math:`x_i`
.. |yi| replace:: :math:`y_i`
.. |ti| replace:: :math:`t_i`
.. |i| replace:: :math:`i`

.. math::

   v_i = \frac{\sqrt{(x_{i} - x_{i-1})^2 + (y_{i} - y_{i-1})^2}}{t_{i} - t_{i-1}}

where (|xi|, |yi|) are the coordinates and (|ti|) is the timestamp of point (|i|).

The function :py:func:`~pywib.velocity_metrics` computes velocity metrics such as mean, max, and min of the velocity for each session.


Acceleration
------------

The acceleration is the rate of change of velocity with respect to time, which provides insights into how quickly users change their speed during interactions :cite:p:`Kieslich2019-mt,Katerina2018-ch`.

The function :py:func:`~pywib.acceleration` computes the acceleration based on the change in velocity over time from a DataFrame or session traces.

The acceleration is calculated as:

.. |vi| replace:: :math:`v_i`
.. math::

   a_i = \frac{v_{i} - v_{i+1}}{t_{i} - t_{i+1}}

where \(|vi|\) is the velocity at point \(|i|\) and \(|ti|\) is the timestamp of point \(|i|\).

Maximum, minimum, and mean acceleration metrics for each session can be computed using the function :py:func:`~pywib.acceleration_metrics`.

Jerkiness
---------

The function :py:func:`~pywib.jerkiness` computes the jerkiness of interaction points from a DataFrame or session traces, based on the change in acceleration over time.

The jerkiness is calculated as the change in acceleration per unit time:

.. |ai| replace:: :math:`a_i`
.. math::

   j_i = \frac{a_{i} - a_{i+1}}{t_{i} - t_{i+1}}

where \(|ai|\) is the acceleration at point \(|i|\) and \(|ti|\) is the timestamp of point \(|i|\).

The function :py:func:`~pywib.jerkiness_metrics` computes jerkiness metrics such as mean, max, and min jerkiness for each session.

References
----------
.. bibliography::
   :style: apa