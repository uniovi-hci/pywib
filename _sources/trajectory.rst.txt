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

AUC Ratio
---------
The Area Under the Curve (AUC) is a metric that quantifies the overall movement efficiency during user interactions in computers :cite:p:`Kieslich2019-mt,Katerina2018-ch` or even in mobile devices :cite:p:`Rhim2023-uz`.

The function :py:func:`~pywib.auc_ratio` calculates the AUC ratio for each session.

That is, the real area under the curve and the optimal area (straight-line) and returns the ratio between their difference and the rael area.

.. |A_real| replace:: :math:`A_{real}`
.. |A_opt| replace:: :math:`A_{opt}`

Given the real area |A_real| and the optimal area |A_opt| the AUC ratio is computed as:

.. math::

   AUC Ratio = \frac{|A_{real} - A_{opt}|}{|A_{opt}| + 10^{-6}}

This small epsilon prevents division-by-zero when the optimal area is 0.

Metrics are also provided via :py:func:`~pywib.auc_ratio_metrics`, which computes mean, max, and min AUC and AUC ratio for each session.

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

References
----------
.. bibliography::
   :style: apa