========================
Coordinate Normalization
========================

This utility makes pointer coordinates comparable across sessions that were
recorded under different conditions. It provides two independent steps:

1. **Zoom normalization** (``normalize_zoom`` / ``normalize_zoom_sessions``):
   undoes the effect of browser zoom (Ctrl +, Ctrl -, Ctrl 0, Ctrl + wheel) so
   that coordinates are expressed as if the page had always been at the initial
   zoom level.
2. **Screen-size normalization** (``normalize_coordinates_to_screen``):
   rescales coordinates by the screen size so that sessions recorded on
   different resolutions (and devices) can be compared.

.. contents:: Contents
   :local:
   :depth: 2


Overview
========

.. code-block:: python

   # 1. Remove the effect of browser zoom (each session is processed on its own)
   df = normalize_zoom_sessions(df, browser_name="chrome")

   # 2. Rescale by screen size (each session uses its own screen size)
   df = normalize_coordinates_to_screen(df, mode="diagonal")

.. important::

   **Order matters.** Always apply zoom normalization *before* screen-size
   normalization. The zoom algorithm measures ratios between pixel positions
   and discards measurements whose x value is below ``min_valid_x`` (100 px by
   default). After screen normalization x lies roughly in the range 0-1, so
   every measurement would be discarded.


Zoom normalization
==================

How it works
------------

When the user zooms, the browser fires a ``resize`` event and the page
coordinates (``pageX`` / ``pageY``) are rescaled by the ratio between the old
and the new zoom level. The algorithm reconstructs the zoom level over time:

1. Events related to zoom (wheel/scroll events, window resize events and zoom
   keys such as ``+``, ``-``, ``0``) are grouped into **bursts**. A new burst
   starts when the gap between two consecutive zoom-related events is larger
   than ``max_gap_ms``. Only bursts that contain at least one resize event are
   kept.
2. For each burst, the zoom steps are resolved in one of two ways:

   * **Key zoom** (``key``) – if the number of zoom keys equals the number of
     resize events, each key gives the direction of one step (``in``, ``out``
     or ``reset``) and the new level is the next/previous level in the
     browser's list of discrete zoom steps.
   * **Measured zoom** (``measured``) – the direction is unknown (wheel zoom),
     so the ratio between the x position of the positioned events before and
     after the resize is measured, and the candidate transition whose ratio is
     closest (in log space) is chosen, provided it is within
     ``log_tolerance``.
3. Resizes that cannot be resolved are labelled ``unresolved``. Because the
   error propagates to the following steps, the scale is considered unknown
   from that point on.
4. The cumulative scale is applied to every event with a valid position:
   ``x_normalized = x / cumulative_scale`` (same for y).

Discrete zoom levels
--------------------

Each browser exposes a fixed list of zoom steps. The browser name is matched
case-insensitively as a substring. Unknown browsers fall back to the Chromium
steps.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Browser
     - Zoom steps
   * - Chrome, Edge, Opera
     - 0.25, 0.33, 0.5, 0.67, 0.75, 0.8, 0.9, 1, 1.1, 1.25, 1.5, 1.75, 2, 2.5,
       3, 4, 5
   * - Firefox
     - 0.3, 0.5, 0.67, 0.8, 0.9, 1, 1.1, 1.2, 1.33, 1.5, 1.7, 2, 2.4, 3, 4, 5
   * - Safari
     - 0.5, 0.75, 0.85, 1, 1.15, 1.25, 1.5, 1.75, 2, 3, 4, 5 (verify against
       the versions you support)

API
---

.. py:function:: normalize_zoom(trace_df, browser_name="", max_gap_ms=150, log_tolerance=0.04, min_valid_x=100, initial_zoom_factor=1.0, zoom_key_mask=None, keep_diagnostics=False)

   Normalize the coordinates of **one session** so that they do not depend on
   the browser zoom. Raises ``ValueError`` if the trace contains more than one
   ``SESSION_ID``.

   :param pandas.DataFrame trace_df: The trace of a single session. It must
      contain the columns ``TIME_STAMP``, ``EVENT_TYPE``, ``KEY_VALUE``, ``X``
      and ``Y`` (see ``ColumnNames``).
   :param str browser_name: Browser used in the session (only one). Case
      insensitive. One of ``chrome``, ``edge``, ``opera``, ``firefox`` or
      ``safari``. Empty or unknown names use the Chromium steps.
   :param int max_gap_ms: Maximum gap, in milliseconds, between consecutive
      zoom-related events (scroll, wheel, resize, zoom key) to consider them
      part of the same zoom burst.
   :param float log_tolerance: Maximum distance, in log space, between the
      measured ratio and the nearest candidate zoom ratio. ``0.04`` is about
      4 %.
   :param int min_valid_x: Minimum x position (px) of the event *before* a
      resize for a measurement to be trusted. Near the left edge the ratio is
      numerically unreliable.
   :param float initial_zoom_factor: Zoom the session started with. The
      closest level in the browser's list is used. ``1.0`` means 100 %.
   :param zoom_key_mask: Optional function that receives the trace and returns
      a boolean Series. Only keyboard events where it is ``True`` count as zoom
      keys. Use it to require the Ctrl/Cmd modifier and to keep only key-down
      events, so that typing ``+``, ``-`` or ``0`` in a text field is not
      interpreted as zoom.
   :param bool keep_diagnostics: If ``True``, keep the ``zoom_classification``,
      ``zoom_break`` and ``cumulative_scale`` columns (see below).
   :returns: The trace, sorted by timestamp (stable sort, index reset), with
      ``X`` and ``Y`` replaced by their zoom-normalized values. Events with
      the ``-1`` sentinel (no position) are left untouched.
   :rtype: pandas.DataFrame

.. py:function:: normalize_zoom_sessions(df, browser_name="", **kwargs)

   Apply ``normalize_zoom`` independently to each session (grouped by
   ``SESSION_ID``). The zoom state is never shared between sessions.

   :param pandas.DataFrame df: Data of one or more sessions.
   :param str browser_name: Browser used in all the sessions.
   :param kwargs: Any other keyword argument accepted by ``normalize_zoom``.
   :returns: The concatenation of the normalized sessions, with the index
      reset. Rows are sorted by timestamp within each session.
   :rtype: pandas.DataFrame

Diagnostic columns
------------------

``normalize_coordinates_for_zoom`` (and ``normalize_zoom`` with
``keep_diagnostics=True``) expose how each resize was resolved:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Column
     - Meaning
   * - ``zoom_classification``
     - ``"key"``, ``"measured"`` or ``"unresolved"`` on each resize row, empty
       elsewhere.
   * - ``zoom_break``
     - ``True`` from the first unresolved resize onward. The scale is unknown
       from there, so the following coordinates should be treated with care
       or discarded.
   * - ``cumulative_scale``
     - Product of the old/new zoom ratios up to each row.

Helper functions
----------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Function
     - Purpose
   * - ``get_zoom_levels_for_browser``
     - Returns the array of zoom steps for a browser name.
   * - ``find_zoom_bursts``
     - Groups wheel/scroll/resize/zoom-key events into bursts and keeps those
       containing a resize. Also returns the direction (``in``/``out``/
       ``reset``) of each genuine zoom key.
   * - ``find_anchor_events``
     - Selects the positioned events used to measure a ratio: the last one
       before the burst, those inside it, and the first one after it.
   * - ``list_possible_zoom_transitions``
     - Lists candidate ``(new_level_index, ratio)`` pairs, where
       ``ratio = old zoom / new zoom``.
   * - ``choose_zoom_transition``
     - Picks the transition to apply, either from the key direction or from
       the measured ratio. Returns ``(new_level_index, ratio)`` or ``None``.

Limitations
-----------

* The ratio of a wheel zoom is measured from the x positions around the
  resize. It assumes that the pointer did not move and that there was no
  horizontal scroll in between; otherwise the ratio is contaminated (the
  ``log_tolerance`` only mitigates this partially).
* Zoom steps are discrete, which is how desktop browsers behave. Pinch zoom on
  mobile and tablet is continuous (visual viewport) and is **not** modelled.
* Zoom keys are detected by their key value only. Pass ``zoom_key_mask`` if your
  trace records the Ctrl/Cmd modifier or distinguishes key-down from key-up
  events; otherwise typing ``+``, ``-`` or ``0`` can be mistaken for zoom, and
  repeated key events can make the key count differ from the resize count (the
  burst is then resolved by measurement).
* After an unresolved resize the scale is unknown (``zoom_break``).


Screen-size normalization
=========================

``normalize_coordinates_to_screen`` normalizes every session with its own
screen size. By default the screen size of a session is the most frequent
(mode) value of ``SCREEN_WIDTH`` and ``SCREEN_HEIGHT``.

API
---

.. py:function:: normalize_coordinates_to_screen(df, x_col=ColumnNames.X, y_col=ColumnNames.Y, mode="diagonal", unit="normalized", pixelsX=1920, pixelsY=1080, screen_size_source="mode")

   Normalize pointer coordinates by screen size, independently for each
   session.

   :param pandas.DataFrame df: Data of one or more sessions. It must pass
      ``validate_dataframe`` and contain ``SESSION_ID``, ``SCREEN_WIDTH``,
      ``SCREEN_HEIGHT`` and the coordinate columns.
   :param str x_col: Name of the x coordinate column.
   :param str y_col: Name of the y coordinate column.
   :param str mode: ``"diagonal"`` (default) or ``"per_axis"``. See
      :ref:`normalization-modes`.
   :param str unit: ``"normalized"`` (default) returns unit-less values.
      ``"pixels"`` multiplies the normalized values back by a reference
      resolution of ``pixelsX`` x ``pixelsY``.
   :param int pixelsX: Reference width in pixels (only used with
      ``unit="pixels"``).
   :param int pixelsY: Reference height in pixels (only used with
      ``unit="pixels"``).
   :param str screen_size_source: How the screen size of each session is
      chosen. ``"mode"`` (default) uses the most frequent value. ``"first"``
      uses the first valid value in row order; use it (after sorting by
      timestamp) when the reported screen size changes with the browser zoom
      during the session, since the first value corresponds to the initial
      zoom.
   :returns: A copy of ``df`` with ``x_col`` and ``y_col`` replaced by the
      normalized values. The ``-1`` sentinels (events with no position) are
      preserved. If the screen size of a session is missing or not positive,
      the coordinates of its positioned events become ``NaN``.
   :rtype: pandas.DataFrame
   :raises ValueError: If ``mode``, ``unit`` or ``screen_size_source`` are
      invalid, or if a required column is missing.

.. _normalization-modes:

Normalization modes
-------------------

``mode="diagonal"``
   ``x / d`` and ``y / d``, with ``d = sqrt(w**2 + h**2)``. The same scale is
   applied to both axes, so the geometry is preserved: circles stay circles,
   and distances, velocities, angles and curvature remain comparable across
   devices. It is also invariant to rotation (``w`` and ``h`` swap but the
   diagonal does not). Use it for **distances and movement features**. Values
   do **not** fill the range 0-1 (see below).

``mode="per_axis"``
   ``x / w`` and ``y / h``. Values fill 0-1 in both axes, but the scale of each
   axis differs, so the space is **anisotropic**. Use it for **positions,
   heatmaps and regions** within devices that share a similar aspect ratio.

Why ``diagonal`` does not fill 0-1
----------------------------------

The diagonal is always longer than either side of the screen. For a point
inside the screen:

* ``x`` in ``[0, w]`` gives ``x / d`` in ``[0, w / d]``, with ``w / d < 1``.
* ``y`` in ``[0, h]`` gives ``y / d`` in ``[0, h / d]``, with ``h / d < 1``.

Moreover, ``w / d`` and ``h / d`` are the cosine and the sine of the angle
between the diagonal and the horizontal, so ``(w/d)**2 + (h/d)**2 = 1``: when
one is close to 1 the other is small. For a 1920x1080 screen the maximum values
are 0.87 (x) and 0.49 (y); for a square screen they are 0.71 in both axes. The
bound 1 is never reached. This is the price of using a single scale for both
axes: the screen remains a rectangle with its original aspect ratio inside the
unit square instead of being stretched to fill it.

What happens when the aspect ratio differs
------------------------------------------

The following table shows three typical devices (in CSS pixels).

.. list-table::
   :header-rows: 1
   :widths: 22 14 22 21 21

   * - Device
     - Diagonal
     - ``diagonal``: max x / max y
     - ``per_axis``: 0.1 in x
     - ``per_axis``: 0.1 in y
   * - Desktop 1920x1080
     - 2203
     - 0.87 / 0.49
     - 192 px
     - 108 px
   * - Tablet 1280x800
     - 1509
     - 0.85 / 0.53
     - 128 px
     - 80 px
   * - Mobile 390x844
     - 930
     - 0.42 / 0.91
     - 39 px
     - 84 px

* With ``diagonal``, the bottom-right corner is (0.87, 0.49) on desktop and
  (0.42, 0.91) on mobile. Distances are comparable, but positions are not, so
  it is unsuitable for heatmaps or regions across aspect ratios.
* With ``per_axis``, the same normalized offset in x and in y corresponds to
  different physical distances, and the relation inverts between landscape and
  portrait devices. Euclidean distances, angles and curvature are distorted.
* With ``unit="pixels"`` and ``per_axis``, mapping a 390x844 screen to
  1920x1080 stretches x by 4.9 and y by 1.28 (a 3.8x deformation between
  axes). With ``diagonal`` the factor is uniform (2.37), so there is no
  distortion, although the result may exceed 1080 in y.

.. note::

   Both modes normalize by *relative* screen size, not by physical size. A
   diagonal fraction of 0.1 is about 2.4" on a 24" monitor and about 0.6" on a
   phone. This is appropriate if the hypothesis is "what fraction of the screen
   did the pointer travel", but not for motor-effort analysis (e.g. Fitts' law).
   Mouse and touch are also different interactions that no normalization
   equates.


Recommendations
===============

* **Distances, velocities and trajectories**: use ``mode="diagonal"``.
* **Positions and heatmaps across devices**: do not mix aspect ratios in the
  same map. Group sessions by device class or orientation and use
  ``mode="per_axis"`` inside each group. For long pages, normalize y by the
  document height or use ``clientY`` instead of ``pageY``.
* **Keep covariates**: store ``aspect_ratio`` and orientation per session so
  they can be controlled for in the analysis.
* **Apply zoom normalization first**, then screen normalization (see the note
  at the top of this document).
* **Check how the screen size behaves with zoom** in your capture. If
  ``SCREEN_WIDTH`` / ``SCREEN_HEIGHT`` change when the user zooms, use
  ``screen_size_source="first"`` on data sorted by timestamp.
* **Avoid** ``unit="pixels"`` with ``per_axis`` when the source and target
  aspect ratios differ.


Caveats and pitfalls
====================

* **Coordinates are ``pageX`` / ``pageY``**, not ``clientX`` / ``clientY``.
  ``y`` therefore includes the scroll offset and can be much larger than
  ``screen_height``; ``x`` can exceed ``screen_width`` with horizontal scroll.
  With ``per_axis``, y / h is not bounded by 1. Normalizing by the screen
  rather than the viewport also adds noise when the window is not maximized.
* **One screen size per session.** If the screen size changes within a session
  (rotation on tablet/mobile), part of the events is normalized with the wrong
  value. ``diagonal`` is robust to rotation; ``per_axis`` is not.
* **Columns are overwritten.** ``normalize_coordinates_to_screen`` replaces
  ``x_col`` and ``y_col``, and ``normalize_zoom`` replaces ``X`` and ``Y``.
  Applying a step twice normalizes twice.
* **Zoom normalization works on one session at a time.** Use
  ``normalize_zoom_sessions`` for several sessions.