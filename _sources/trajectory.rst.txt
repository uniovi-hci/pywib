Trajectory Metrics
==================

This section covers various trajectory metrics used to analyze the users trajectory, such as path length or AUC, which provide insights into movement efficiency and accuracy during user interactions in a mathematically rigorous manner.

.. currentmodule:: pywib

Path
----
The path or total distance traveled during user interactions is a key metric for analyzing movement efficiency :cite:p:`Kieslich2019-mt,Katerina2018-ch,Rhim2023-uz,Seelye2015-yx`.

The function :py:func:`~pywib.path` calculates the path length for interaction points from a DataFrame or session traces.
This function computes the path length based on the Euclidean distance between consecutive points.

The distance between consecutive points is calculated as:

.. math::

   d_i = \sqrt{(x_{i} - x_{i-1})^2 + (y_{i} - y_{i-1})^2}

AUC
---
The Area Under the Curve (AUC) quantifies the overall movement efficiency during user interactions in computers :cite:p:`Kieslich2019-mt,Katerina2018-ch` or even in mobile devices :cite:p:`Rhim2023-uz`.

The function :py:func:`~pywib.auc` computes the AUC for a DataFrame or session traces. The current implementation returns a tuple of geometric AUC and execution AUC when operating on a single DataFrame, and a dictionary keyed by session containing lists of those two values when operating trace-wise.

In other words, for each trajectory segment it evaluates the area under the curve considering both the geometric path and the execution-time profile of the movement. This allows one to compare the actual trajectory geometry against the temporal execution of the interaction.

Metrics such as mean, maximum, and minimum AUC values can still be summarized afterward from the per-session outputs when needed.

Maximum Absolute Deviation
----------------------------

The Maximum Absolute Deviation (MAD) is a metric that quantifies the maximum deviation of the actual movement path from the optimal straight-line path during user interactions :cite:p:`Kieslich2019-mt,Katerina2018-ch,Rhim2023-uz`.

The function :py:func:`~pywib.deviations` calculates the MAD for each session or interaction trace, returning both the mean, maximum and minimum MAD values.

The MAD is calculated as the maximum perpendicular distance from any point on the actual path to the straight line connecting the start and end points of the movement.

.. figure:: /_static/images/mad_diagram.svg
   :alt: Diagram illustrating Maximum Absolute Deviation (MAD)
   :align: center

   Diagram illustrating Maximum Absolute Deviation (MAD)

Average Absolute Deviation
--------------------------

The Average Absolute Deviation (AAD) is a metric that quantifies the average deviation of the actual movement path from the optimal straight-line path during user interactions :cite:p:`Rhim2023-uz`.

It consists of the average value of the perpendicular distances from each point of the trajectory to the straight line connecting the start and end points of the movement (optimal trajectory).

The function :py:func:`~pywib.deviations` calculates the AAD for each session or interaction trace, returning the AAD value along with MAD metrics.

.. figure:: /_static/images/aad_diagram.svg
   :alt: Diagram illustrating Average Absolute Deviation (AAD)
   :align: center

   Diagram illustrating Average Absolute Deviation (AAD)

Direction Changes
-----------------
The number of direction changes is a metric that quantifies how often the movement direction reverses or shifts substantially during a trajectory.

The function :py:func:`~pywib.direction_changes` computes the direction of each displacement vector from :math:`\Delta x` and :math:`\Delta y`, then evaluates the angular difference between consecutive steps. A direction change is counted when the absolute angular difference exceeds 45 degrees, i.e., more than :math:`\pi / 4` radians.

This metric is directly related to its submetrics :py:func:`~pywib.x_flips` and :py:func:`~pywib.y_flips`, which count directional reversals along the x-axis and y-axis, respectively.

X-direction Flips
-----------------
The function :py:func:`~pywib.x_flips` counts how many times the x-component of movement changes sign beyond a given threshold. In the implementation, the threshold is set by default to 0.1, and the metric is computed from the displacement along the x-axis, :math:`\Delta x`.

This captures horizontal reversals in movement, such as when the cursor starts moving left after having moved right, or vice versa.

.. note::

   Context specificity: when computed on traces, the function sums the flips across all traces in each session. A flip occurring between the end of one trace and the beginning of the next one is not counted, because the computation is performed trace by trace. To include those transitions, compute the metric on the full dataframe or combine the traces into a single movement sequence.

Y-direction Flips
-----------------
The function :py:func:`~pywib.y_flips` follows the same logic as :py:func:`~pywib.x_flips`, but applied to the y-component of movement, :math:`\Delta y`.

It counts the number of times the vertical direction changes sign beyond the configured threshold, which is useful for detecting upward and downward reversals in the trajectory.

.. note::

   Context specificity: when computed on traces, the function sums the flips across all traces in each session. A flip occurring between the end of one trace and the beginning of the next one is not counted, because the computation is performed trace by trace. To include those transitions, compute the metric on the full dataframe or integrate the traces into a single trajectory.


References
----------
.. bibliography::
   :style: apa