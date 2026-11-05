Visualization
=============

.. currentmodule:: pywib

Introduction
------------
Visualizing user interaction data is often essential for interpreting results, validating segmentation, or supporting analyses carried out using computer vision techniques.
**PyWIB** provides a set of visualization utilities, built on top of `seaborn <https://seaborn.pydata.org/>`_ and `matplotlib <https://matplotlib.org/>`_, that allow researchers to generate visual representations of mouse trajectories and keystroke activity without relying on external, paywalled tools.

These utilities can be used either on a full session DataFrame or on individual segmented traces (see :doc:`segmentation`), depending on whether the goal is to inspect an entire session or a specific movement episode.

Trace Visualization
--------------------
The function :py:func:`~pywib.visualize_trace` generates an image representing the user's mouse movement over the screen, plotting the recorded coordinates as a path.

This function accepts either:

- a full DataFrame containing the entirety of a user's interaction, or
- a single segmented trace, to focus the visualization on a specific movement episode.

.. figure:: /_static/images/trace_visualization_example.png
   :alt: Example of a mouse trace visualization
   :align: center

   Example output of :py:func:`~pywib.visualize_trace`, showing recorded mouse movement over the screen.

Video Generation
------------------
For a more dynamic representation of user interaction, the function :py:func:`~pywib.video_from_trace` generates an ``.mp4`` video from a trace, using the recorded event timestamps to reconstruct the movement over time.

This is particularly useful for reviewing sessions qualitatively, or for use alongside computer vision-based analyses of user behavior.

.. note::
   Video generation relies on timestamp information to reconstruct playback speed accurately. Ensure your DataFrame includes a valid timestamp column before calling this function.

Keystroke Heatmap
--------------------
The function :py:func:`~pywib.keyboard_heatmap` generates a heatmap visualizing typing intensity across the keyboard layout, based on the frequency of key press events recorded during a session.

This visualization is useful for identifying patterns in typing behavior, such as frequently used keys or areas of the keyboard associated with errors (e.g., heavy backspace usage).

.. figure:: /_static/images/keyboard_heatmap_example.png
   :alt: Example of a keystroke heatmap
   :align: center

   Example output of :py:func:`~pywib.keyboard_heatmap`, showing the spatial distribution of key presses.

Notes
------
All visualization functions in this module are intended as exploratory and reporting tools. They are not designed to replace statistical validation of results, but rather to complement it by making patterns in interaction data easier to identify and communicate.

References
----------
.. bibliography::
   :style: apa