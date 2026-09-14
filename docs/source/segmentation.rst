Segmentation
============

.. currentmodule:: pywib

Introduction
------------
Long user sessions typically contain a mix of movement and non-movement events (clicks, keystrokes, pauses, etc.), which makes it difficult to analyze specific portions of user interaction in isolation.
To address this, **PyWIB** provides segmentation utilities that split a session into smaller, meaningful units called **traces**.

Working with traces instead of full sessions allows most movement-related metrics (velocity, acceleration, jerkiness, path, AUC, MAD, AAD) to be computed over a well-defined, continuous portion of interaction, rather than across gaps caused by clicks, pauses, or other non-movement events.

.. note::
   Most trajectory and movement metrics documented in :doc:`movement` and :doc:`trajectory` are designed to operate on traces. Most of these metrics automatically compute the traces from the input dataframe, but you can manually compute the traces using your own segmentation logic if needed.

What is a Trace?
-----------------
A **trace** is defined as a sequence of consecutive, non-stopped mouse or touch movements occurring between two non-movement events.

In other words, a trace begins after a non-movement event (such as a click, a key press, or a pause) and ends when the next non-movement event occurs. This segmentation approach is widely used in HCI research to gain more precise insights into user movement and trajectory patterns.

Movement Segmentation
-----------------------
Movement-based segmentation is implemented through two functions, both of which accept a DataFrame containing interaction event data as input:

- :py:func:`~pywib.extract_trace`: extracts a single list of traces from a DataFrame representing one session.
- :py:func:`~pywib.extract_traces_by_session`: extracts traces across multiple sessions, returning a dictionary where each key is a ``sessionId`` and each value is the corresponding list of traces for that session.

These functions rely on the presence of movement and non-movement event types (see :py:class:`~pywib.constants.EventTypes`) to determine trace boundaries.

Keystroke Segmentation
------------------------
Segmentation is not limited to movement data. **pywib** also provides a method to extract traces of keystroke-only interaction, which is useful when computing metrics such as typing duration or typing speed over isolated typing episodes.

The function :py:func:`~pywib.extract_keystroke_traces_by_session` reduces a DataFrame to a dictionary containing, for each session, a list of segments in which the user's interaction occurs exclusively through the keyboard.

Notes
------
When choosing whether to segment your data before computing metrics, consider the following:

- Unsegmented DataFrames: metrics are computed over the entire session, which may mix distinct movement episodes together.
- Segmented traces: metrics are computed per trace, offering finer-grained insight but requiring an extra preprocessing step.

This distinction is particularly relevant for metrics such as :py:func:`~pywib.num_pauses`, where the behaviour of the computation changes depending on whether the input DataFrame is segmented or not (see :doc:`timing`).

References
----------
.. bibliography::
   :style: apa