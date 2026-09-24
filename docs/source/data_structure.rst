Data structures required to use PyWIB
-------------------------------------

The library operates on a :class:`pandas.DataFrame` in which each row represents
a single interaction event. This page describes the expected columns and shows
an example of a valid input.

Required columns
----------------

Every DataFrame **must** contain the following columns. Missing any of them
will raise an error at validation time.

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Column
     - Type
     - Description
   * - ``sessionId``
     - ``str``
     - Identifier of the session the event belongs to.
   * - ``x``
     - ``float``
     - Horizontal coordinate of the event.
   * - ``y``
     - ``float``
     - Vertical coordinate of the event.
   * - ``timeStamp``
     - ``int``
     - Time at which the event occurred in milliseconds.
   * - ``eventType``
     - ``str``
     - Type of the event as a number identified by one of the :py:class:`~pywib.EventTypes`.

Optional columns
----------------

The following columns are optional. If present, they enable additional
functionality; if absent, the library falls back to default behavior.

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Column
     - Type
     - Description
   * - ``keyValue``
     - ``str``
     - Value of the key associated with a keyboard event.
   * - ``keyCode``
     - ``str``
     - Code of the key associated with a keyboard event.
   * - ``sourceSessionId``
     - ``str``
     - Identifier of the session from which this session originates.
   * - ``elementId``
     - ``str``
     - Identifier of the UI element targeted by the event.
   * - ``sceneId``
     - ``str``
     - Identifier of the scene in which the event took place.

.. note::

   Column names are **case-sensitive** and must match exactly as written above.
   In case of doubt, please use :py:class:`~pywib.ColumnNames`

Example
-------

The following DataFrame contains the required columns plus a few optional ones:

.. code-block:: python

   import pandas as pd

   df = pd.DataFrame({
       "sessionId": ["s1", "s1", "s1", "s2"],
       "x":         [120.0, 245.5, 245.5, 30.0],
       "y":         [80.0, 310.2, 310.2, 415.0],
       "timeStamp": [1700000000, 1700000002, 1700000003, 1700000100],
       "eventType": [0, 0, 13, 1],
       "keyValue":  [-1, -1, "a", -1],
       "keyCode":   [-1, -1, "KeyA", -1],
       "elementId": [-1, -1, "input-name", "btn-exit"],
       "sceneId":   ["intro", "intro", "intro", "outro"],
   })

Which renders as:

.. csv-table::
   :header: "sessionId", "x", "y", "timeStamp", "eventType", "keyValue", "keyCode", "elementId", "sceneId"
   :widths: 10, 8, 8, 14, 12, 10, 10, 14, 10

   "s1", 120.0, 80.0, 1700000000, 0, , , "btn-start", "intro"
   "s1", 245.5, 310.2, 1700000002, 0", , , , "intro"
   "s1", 245.5, 310.2, 1700000003, 13, "a", "KeyA", "input-name", "form"
   "s2", 30.0, 415.0, 1700000100, 1, , , "btn-exit", "outro"

.. note::
    A function that renames columns has been created to ease working with this format.
    See :py:func:`~pywib.to_pywib_df`

Minimal example
^^^^^^^^^^^^^^^

A DataFrame with only the required columns is also valid:

.. code-block:: python

    from pywib import to_pywib_df

    df_minimal = pd.DataFrame({
       "id": ["s1", "s1"],
       "xPos":         [10.0, 20.0],
       "yPos":         [15.0, 25.0],
       "timeStamp": [1700000000, 1700000001],
       "event": [1, 1],
   })
   df_minimal = to_pywib_df(df_minimal, "id", "xPos", "yPos", "timeStamp","event")