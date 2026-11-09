"""
Coordinate normalization utilities.

Two independent steps are provided:

1. Zoom normalization (``normalize_zoom`` / ``normalize_zoom_sessions``): undoes the
   effect of browser zoom so that coordinates are expressed at the initial zoom level.
2. Screen-size normalization (``normalize_coordinates_to_screen``): rescales the
   coordinates by the screen size so that sessions recorded on different devices
   can be compared.

Always apply zoom normalization BEFORE screen-size normalization.
"""
from typing import Callable, Optional

import numpy as np
import pandas as pd

from pywib.constants import ColumnNames, EventTypes
from pywib.utils.validation import validate_dataframe


CHROMIUM_ZOOM_LEVELS = [.25, .33, .5, .67, .75, .8, .9, 1, 1.1, 1.25,
                        1.5, 1.75, 2, 2.5, 3, 4, 5]        # Discrete zoom steps used by Chrome/Edge/Opera

ZOOM_LEVELS_BY_BROWSER_NAME = {
    "chrome": CHROMIUM_ZOOM_LEVELS,                         # Chrome uses the Chromium steps
    "edge": CHROMIUM_ZOOM_LEVELS,                           # Edge uses the Chromium steps
    "opera": CHROMIUM_ZOOM_LEVELS,                          # Opera uses the Chromium steps
    "firefox": [.3, .5, .67, .8, .9, 1, 1.1, 1.2, 1.33,
                1.5, 1.7, 2, 2.4, 3, 4, 5],                 # Firefox steps
    "safari": [.5, .75, .85, 1, 1.15, 1.25, 1.5,
               1.75, 2, 3, 4, 5],                           # Safari steps (verify against your versions)
}

ZOOM_KEY_TO_DIRECTION = {
    "+": "in", "=": "in",                                   # '+' (or '=' on many layouts) zooms in
    "-": "out", "_": "out",                                 # '-' zooms out
    "0": "reset",                                           # Ctrl+0 resets zoom to 100%
}

SCREEN_NORMALIZATION_MODES = ("per_axis", "diagonal")
SCREEN_NORMALIZATION_UNITS = ("normalized", "pixels")
SCREEN_SIZE_SOURCES = ("mode", "first")


# ---------------------------------------------------------------------------
# Zoom normalization
# ---------------------------------------------------------------------------

def get_zoom_levels_for_browser(browser_name: str) -> np.ndarray:
    """
    Return the discrete zoom levels of a browser.

    The name is matched case-insensitively as a substring (e.g. "Microsoft Edge"
    matches "edge"). Unknown or empty names fall back to the Chromium steps.

    Parameters:
        browser_name (str): The browser name to get the zoom levels for. Case insensitive.

    Returns:
        np.ndarray: The zoom levels, as floats, in increasing order.
    """
    browser_name_lower = str(browser_name).lower()
    for known_browser, zoom_levels in ZOOM_LEVELS_BY_BROWSER_NAME.items():
        if known_browser in browser_name_lower:
            return np.array(zoom_levels, float)
    return np.array(CHROMIUM_ZOOM_LEVELS, float)


def list_possible_zoom_transitions(zoom_levels, current_level_index, key_direction, max_level_jump):
    """
    Return the candidate ``(new_level_index, ratio)`` pairs, where ``ratio = old zoom / new zoom``.

    Parameters:
        zoom_levels (np.ndarray): The discrete zoom levels of the browser.
        current_level_index (int): Index of the current zoom level in ``zoom_levels``.
        key_direction (str | None): ``"in"`` / ``"out"`` (exactly one step in that direction),
            ``"reset"`` (go to the level closest to 100 %) or ``None`` (direction unknown:
            every level within ``max_level_jump`` steps is a candidate).
        max_level_jump (int): Maximum number of levels to move when the direction is unknown.

    Returns:
        list[tuple[int, float]]: The candidates. Levels outside the list are discarded.
        Empty if there is no possible transition (e.g. ``"reset"`` while already at 100 %).
    """
    if key_direction == "reset":                             # Ctrl+0: go back to 100%
        reset_level_index = int(np.argmin(np.abs(zoom_levels - 1)))  # Index of the level closest to 1.0
        if reset_level_index != current_level_index:         # Only a transition if the level actually changes
            return [(reset_level_index, zoom_levels[current_level_index] / zoom_levels[reset_level_index])]
        return []                                            # Already at 100%: no transition
    if key_direction in ("in", "out"):                       # Key zoom: exactly one step in a known direction
        level_offsets = [1 if key_direction == "in" else -1]
    else:                                                    # Wheel zoom: direction unknown, try nearby steps
        level_offsets = [k for k in range(-max_level_jump, max_level_jump + 1) if k]  # e.g. -2,-1,1,2 (skip 0)
    return [
        (current_level_index + offset,                       # Candidate new level index
         zoom_levels[current_level_index] / zoom_levels[current_level_index + offset])  # Its old/new zoom ratio
        for offset in level_offsets
        if 0 <= current_level_index + offset < len(zoom_levels)  # Discard levels outside the list
    ]


def choose_zoom_transition(candidate_transitions, measured_ratio, direction_known_from_key, log_tolerance):
    """
    Pick the transition to apply.

    Parameters:
        candidate_transitions (list[tuple[int, float]]): Output of ``list_possible_zoom_transitions``.
        measured_ratio (float): Ratio measured from the positions around the resize
            (old zoom / new zoom). Ignored when ``direction_known_from_key`` is True.
        direction_known_from_key (bool): True if the step comes from a zoom key, in which
            case the (single) candidate is returned as is.
        log_tolerance (float): Maximum allowed ``|log(measured / candidate)|`` for a
            measured transition to be accepted (0.04 is about 4 %).

    Returns:
        tuple[int, float] | None: ``(new_level_index, ratio)``, or None if no candidate
        is available or none is close enough to the measured ratio.
    """
    if not candidate_transitions:                            # No possible transition
        return None
    if direction_known_from_key:                             # Key zoom: the step is unique
        return candidate_transitions[0]
    if not np.isfinite(measured_ratio) or measured_ratio <= 0:  # Wheel zoom needs a valid measurement
        return None
    new_level_index, closest_ratio = min(                    # Candidate whose ratio is closest to the measured one
        candidate_transitions, key=lambda c: abs(np.log(measured_ratio / c[1])))
    if abs(np.log(measured_ratio / closest_ratio)) <= log_tolerance:  # Close enough to a real zoom step
        return new_level_index, closest_ratio
    return None


def find_zoom_bursts(trace_df: pd.DataFrame, max_gap_ms: int = 150,
                     zoom_key_mask: Optional[Callable[[pd.DataFrame], pd.Series]] = None):
    """
    Group wheel / scroll / resize / zoom-key events into bursts; keep bursts containing a resize.

    Parameters:
        trace_df (pd.DataFrame): A single-session trace, sorted by timestamp with a default index.
        max_gap_ms (int): A new burst starts when the gap between two consecutive
            zoom-related events is larger than this value (milliseconds).
        zoom_key_mask (Callable | None): Optional function that receives ``trace_df`` and returns
            a boolean Series. Only keyboard events where it is True count as zoom keys. Use it to
            require the Ctrl/Cmd modifier or to keep only key-down events, so that typing "+", "-"
            or "0" in a text field is not interpreted as zoom.

    Returns:
        tuple[list[pd.DataFrame], pd.Series]: The bursts, and a Series with the zoom direction
        (``"in"`` / ``"out"`` / ``"reset"``) of each zoom key event and NaN elsewhere.
    """
    key_direction = trace_df[ColumnNames.KEY_VALUE].astype(str).map(ZOOM_KEY_TO_DIRECTION)   # 'in'/'out'/'reset' or NaN
    is_zoom_key = trace_df[ColumnNames.EVENT_TYPE].isin(EventTypes.KEYBOARD_EVENTS_LIST) & key_direction.notna()
    if zoom_key_mask is not None:                            # Caller-defined extra filter (modifier, key-down...)
        extra_mask = pd.Series(zoom_key_mask(trace_df), index=trace_df.index).astype(bool)
        is_zoom_key = is_zoom_key & extra_mask
    key_direction = key_direction.where(is_zoom_key)         # Only genuine zoom keys keep a direction
    is_zoom_related = (trace_df[ColumnNames.EVENT_TYPE].isin(EventTypes.SCROLL_EVENTS_LIST + [EventTypes.EVENT_WINDOW_RESIZE])
                       | is_zoom_key)                        # Every event that can belong to a zoom
    zoom_related_events = trace_df[is_zoom_related]          # Mouse moves and other events are ignored here
    burst_id = (zoom_related_events[ColumnNames.TIME_STAMP].diff() > max_gap_ms).cumsum()  # New burst after a long gap
    bursts = [burst for _, burst in zoom_related_events.groupby(burst_id)
              if (burst[ColumnNames.EVENT_TYPE] == EventTypes.EVENT_WINDOW_RESIZE).any()]  # A zoom always emits a resize
    return bursts, key_direction


def find_anchor_events(trace_df, burst, has_position):
    """
    Positioned events to measure with: last one before the burst, those inside it, first one after it.

    Parameters:
        trace_df (pd.DataFrame): The sorted single-session trace.
        burst (pd.DataFrame): One burst returned by ``find_zoom_bursts``.
        has_position (pd.Series): Boolean mask of the events that carry a real position.

    Returns:
        pd.DataFrame: The anchor events, in row order.
    """
    first_index, last_index = burst.index[0], burst.index[-1]                      # Row range of the burst
    before_burst = trace_df[has_position & (trace_df.index < first_index)].tail(1)  # Last known position before
    inside_burst = trace_df[has_position & (trace_df.index >= first_index) & (trace_df.index <= last_index)]
    after_burst = trace_df[has_position & (trace_df.index > last_index)].head(1)    # First known position after
    return pd.concat([before_burst, inside_burst, after_burst])                    # Already in row order


def normalize_coordinates_for_zoom(trace_df: pd.DataFrame, browser_name: str = "", max_gap_ms: int = 150,
                                   log_tolerance: float = 0.04, min_valid_x: int = 100,
                                   initial_zoom_factor: float = 1.0,
                                   zoom_key_mask: Optional[Callable[[pd.DataFrame], pd.Series]] = None) -> pd.DataFrame:
    """
    Reconstruct the zoom level over time for ONE session and divide the coordinates by the cumulative scale.

    The trace is sorted by timestamp (stable sort) and its index is reset. Each resize inside a
    zoom burst is resolved either from the zoom key that caused it (``"key"``), from the ratio
    between the x position before and after it (``"measured"``), or left ``"unresolved"``.

    Parameters:
        trace_df (pd.DataFrame): The trace of a single session. Raises ``ValueError`` if it
            contains more than one ``SESSION_ID``; use ``normalize_zoom_sessions`` instead.
        browser_name (str): Browser of the session. See ``get_zoom_levels_for_browser``.
        max_gap_ms (int): Maximum gap between consecutive zoom-related events (scroll, wheel,
            resize, zoom key) to consider them part of the same zoom burst.
        log_tolerance (float): Maximum ``|log(measured ratio / zoom step ratio)|`` to accept a
            measured step. 0.04 is about 4 %.
        min_valid_x (int): Minimum x (px) of the positioned event before a resize for its ratio
            to be trusted. Near the left edge the ratio is numerically unreliable.
        initial_zoom_factor (float): Zoom the session started with (1.0 is 100 %). The closest
            level in the browser's list is used.
        zoom_key_mask (Callable | None): See ``find_zoom_bursts``.

    Returns:
        pd.DataFrame: A copy of the trace with these extra columns:

        - ``zoom_classification``: ``"key"``, ``"measured"`` or ``"unresolved"`` on each resize
          row, empty elsewhere.
        - ``zoom_break``: True from the first unresolved resize onward (the scale is unknown
          from there on, because the error propagates to the following steps).
        - ``cumulative_scale``: product of the old/new zoom ratios up to each row.
        - ``x_normalized`` / ``y_normalized``: coordinates divided by ``cumulative_scale``.
          Events without a position (``-1`` sentinel) are left untouched.
    """
    if (ColumnNames.SESSION_ID in trace_df.columns
            and trace_df[ColumnNames.SESSION_ID].nunique() > 1):
        raise ValueError("The trace contains more than one session. "
                         "Use normalize_zoom_sessions to process each session independently.")

    zoom_levels = get_zoom_levels_for_browser(browser_name)                   # Zoom steps of this browser
    sorted_trace = trace_df.copy()
    sorted_trace[ColumnNames.TIME_STAMP] = pd.to_numeric(sorted_trace[ColumnNames.TIME_STAMP], errors="coerce")
    sorted_trace = sorted_trace.sort_values(ColumnNames.TIME_STAMP, kind="stable").reset_index(drop=True)
    x_positions = sorted_trace[ColumnNames.X].to_numpy(float)                 # pageX values
    has_position = (sorted_trace[ColumnNames.EVENT_TYPE].isin([EventTypes.EVENT_ON_MOUSE_MOVE, EventTypes.EVENT_ON_WHEEL])
                    & (sorted_trace[ColumnNames.X] > -1) & (sorted_trace[ColumnNames.Y] > -1))  # Events that carry a real position

    current_level_index = int(np.argmin(np.abs(zoom_levels - initial_zoom_factor)))  # Starting zoom level
    ratio_per_event = np.ones(len(sorted_trace))                              # Scale change at each row
    classification_per_event = np.full(len(sorted_trace), "", dtype=object)   # How each resize was resolved
    minimum_trusted_x = max(min_valid_x, np.finfo(float).eps)                 # Never divide by (almost) zero

    bursts, key_direction = find_zoom_bursts(sorted_trace, max_gap_ms, zoom_key_mask)
    for burst in bursts:
        resize_indices = burst.index[burst[ColumnNames.EVENT_TYPE] == EventTypes.EVENT_WINDOW_RESIZE]  # Zoom steps in this burst
        burst_key_directions = key_direction[burst.index].dropna().tolist()   # Zoom keys pressed in the burst

        if len(burst_key_directions) == len(resize_indices):                  # One key per resize: steps are known
            for resize_index, direction in zip(resize_indices, burst_key_directions):
                candidates = list_possible_zoom_transitions(zoom_levels, current_level_index, direction, 1)
                resolution = choose_zoom_transition(candidates, np.nan, True, log_tolerance)
                if resolution is None:
                    classification_per_event[resize_index] = "unresolved"
                    continue
                current_level_index, ratio_per_event[resize_index] = resolution
                classification_per_event[resize_index] = "key"
            continue

        anchors = find_anchor_events(sorted_trace, burst, has_position)       # Positioned events around the burst
        resolved_resizes = set()                                              # Resizes covered by a measurement
        for anchor_before, anchor_after in zip(anchors.index[:-1], anchors.index[1:]):
            resizes_between = resize_indices[(resize_indices > anchor_before) & (resize_indices < anchor_after)]
            if len(resizes_between) == 0:                                     # No zoom step between these two
                continue
            if not x_positions[anchor_before] >= minimum_trusted_x:           # Near the left edge (or NaN): ratio unreliable
                continue
            measured_ratio = x_positions[anchor_after] / x_positions[anchor_before]  # Old zoom / new zoom
            candidates = list_possible_zoom_transitions(
                zoom_levels, current_level_index, None, len(resizes_between)) # Net change of -k..k levels
            if len(resizes_between) >= 2:                                     # In + out cancel each other
                candidates.append((current_level_index, 1.0))
            resolution = choose_zoom_transition(candidates, measured_ratio, False, log_tolerance)
            if resolution is None:                                            # No step combination fits
                continue
            current_level_index, ratio_per_event[resizes_between[-1]] = resolution  # Whole change on last resize
            classification_per_event[resizes_between] = "measured"            # All steps of this span are resolved
            resolved_resizes.update(resizes_between)
        for resize_index in resize_indices:                                   # Anything not covered stays unknown
            if resize_index not in resolved_resizes:
                classification_per_event[resize_index] = "unresolved"

    sorted_trace["zoom_classification"] = classification_per_event
    sorted_trace["zoom_break"] = np.cumsum(classification_per_event == "unresolved") > 0  # Scale unknown from the first failure on
    sorted_trace["cumulative_scale"] = np.cumprod(ratio_per_event)
    has_valid_position = (sorted_trace[ColumnNames.X] > -1) & (sorted_trace[ColumnNames.Y] > -1)
    sorted_trace["x_normalized"] = np.where(has_valid_position, sorted_trace[ColumnNames.X] / sorted_trace["cumulative_scale"], sorted_trace[ColumnNames.X])
    sorted_trace["y_normalized"] = np.where(has_valid_position, sorted_trace[ColumnNames.Y] / sorted_trace["cumulative_scale"], sorted_trace[ColumnNames.Y])
    return sorted_trace


def normalize_zoom(trace_df: pd.DataFrame, browser_name: str = "", max_gap_ms: int = 150,
                   log_tolerance: float = 0.04, min_valid_x: int = 100, initial_zoom_factor: float = 1.0,
                   zoom_key_mask: Optional[Callable[[pd.DataFrame], pd.Series]] = None,
                   keep_diagnostics: bool = False) -> pd.DataFrame:
    """
    Normalize the coordinates of ONE session so that they do not depend on the browser zoom.

    Zoom (Ctrl +, Ctrl -, Ctrl 0, Ctrl + wheel) rescales the page coordinates (pageX / pageY).
    This function reconstructs the zoom level over time and divides the coordinates by the
    cumulative scale, so that every position is expressed at the initial zoom level. It must be
    applied BEFORE ``normalize_coordinates_to_screen``.

    The returned trace is sorted by timestamp (stable sort) and its index is reset.

    Parameters:
        trace_df (pd.DataFrame): The trace of a single session. Use ``normalize_zoom_sessions``
            for a DataFrame with several sessions.
        browser_name (str): The browser used in the session (only one). Case insensitive. One of:
            chrome, edge, opera, firefox or safari. Empty or unknown names use the Chromium steps.
        max_gap_ms (int): Maximum gap, in milliseconds, between consecutive zoom-related events
            (scroll, wheel, resize, zoom key) to consider them part of the same zoom burst.
        log_tolerance (float): Maximum distance, in log space, between the measured ratio and the
            nearest zoom step ratio. 0.04 is about 4 %.
        min_valid_x (int): Minimum x position (px) of the event before a resize for a measurement
            to be trusted.
        initial_zoom_factor (float): The zoom the session started with. By default 1.0 (100 %).
        zoom_key_mask (Callable | None): Optional function receiving the trace and returning a
            boolean Series; only keyboard events where it is True count as zoom keys (e.g. the
            Ctrl/Cmd modifier is pressed and the event is a key-down).
        keep_diagnostics (bool): If True, keep the ``zoom_classification``, ``zoom_break`` and
            ``cumulative_scale`` columns. If False (default) they are dropped.

    Returns:
        pd.DataFrame: The trace with ``X`` and ``Y`` replaced by their zoom-normalized values.
        Events with the ``-1`` sentinel (no position) are left untouched.

    Limitations:
        - The ratio of a wheel zoom is measured from the x positions around the resize, so it
          assumes the pointer did not move and there was no horizontal scroll in between.
        - Zoom steps are discrete (desktop browsers). Pinch zoom on mobile/tablet is continuous
          and is not modelled.
    """
    df = normalize_coordinates_for_zoom(trace_df=trace_df, browser_name=browser_name, max_gap_ms=max_gap_ms,
                                        log_tolerance=log_tolerance, min_valid_x=min_valid_x,
                                        initial_zoom_factor=initial_zoom_factor, zoom_key_mask=zoom_key_mask)

    df[ColumnNames.X] = df["x_normalized"]
    df[ColumnNames.Y] = df["y_normalized"]

    columns_to_drop = ["x_normalized", "y_normalized"]
    if not keep_diagnostics:
        columns_to_drop += ["cumulative_scale", "zoom_break", "zoom_classification"]
    return df.drop(columns=columns_to_drop)


def normalize_zoom_sessions(df: pd.DataFrame, browser_name: str = "", **kwargs) -> pd.DataFrame:
    """
    Apply ``normalize_zoom`` independently to each session (grouped by ``SESSION_ID``).

    The zoom state (current level, cumulative scale) is never shared between sessions.

    Parameters:
        df (pd.DataFrame): Data of one or more sessions.
        browser_name (str): Browser used in all the sessions. See ``normalize_zoom``.
        **kwargs: Any other keyword argument accepted by ``normalize_zoom``.

    Returns:
        pd.DataFrame: The concatenation of every normalized session, with the index reset.
        Rows are sorted by timestamp within each session; sessions keep their order of appearance.
    """
    validate_dataframe(df)
    sessions = df.groupby(ColumnNames.SESSION_ID, sort=False, dropna=False)
    return pd.concat(
        (normalize_zoom(session_df, browser_name=browser_name, **kwargs) for _, session_df in sessions),
        ignore_index=True,
    )


# ---------------------------------------------------------------------------
# Screen-size normalization
# ---------------------------------------------------------------------------

def _most_frequent(values: pd.Series):
    """Most frequent value of a Series, or NaN if the Series has no valid values."""
    modes = values.mode()
    return modes.iloc[0] if not modes.empty else np.nan


def normalize_coordinates_to_screen(df: pd.DataFrame,
                                    x_col: str = ColumnNames.X,
                                    y_col: str = ColumnNames.Y,
                                    mode: str = "diagonal",
                                    unit: str = "normalized",
                                    pixelsX: int = 1920,
                                    pixelsY: int = 1080,
                                    screen_size_source: str = "mode") -> pd.DataFrame:
    """
    Normalize pointer coordinates by screen size, independently for each session.

    Modes:
        - ``"diagonal"``: ``x / d`` and ``y / d``, where ``d = sqrt(w**2 + h**2)``.
          The same scale is applied to both axes, so the geometry is preserved
          (distances, velocities and angles stay comparable across devices and
          orientations). Use it for distances and movement features.
          The values do NOT fill the range 0-1: for coordinates inside the screen,
          ``x`` lies in ``[0, w/d]`` and ``y`` in ``[0, h/d]``, and both bounds
          are below 1 (e.g. 1920x1080 -> x max 0.87, y max 0.49).
        - ``"per_axis"``: ``x / w`` and ``y / h``. Each axis fills 0-1, but the
          scale differs per axis, so distances and angles are distorted when
          aspect ratios differ. Use it for positions, heatmaps and regions
          within devices that share a similar aspect ratio.

    Units:
        - ``"normalized"``: the unit-less values described above.
        - ``"pixels"``: the normalized values are multiplied by a reference
          resolution of ``pixelsX`` x ``pixelsY`` (by its diagonal in
          ``"diagonal"`` mode). Avoid ``"per_axis"`` with this unit when the
          source and reference aspect ratios differ, since it stretches each
          axis by a different factor.

    Notes:
        - Events with the ``-1`` sentinel (no position) are kept unchanged.
        - Every session must have a valid screen size (width and height greater
          than 0). Otherwise a ``ValueError`` listing the offending sessions is
          raised, so that they can be fixed or removed before normalizing.
        - ``x_col`` and ``y_col`` are overwritten in the returned copy; applying
          the function twice normalizes twice. The input DataFrame is not modified.
        - Both modes use relative screen size, not physical size.
        - If the coordinates are ``pageX`` / ``pageY``, ``y`` includes the scroll
          offset and may exceed the screen height, so values can fall outside
          the ranges above.
        - Apply zoom normalization (``normalize_zoom``) before this function.

    Parameters:
        df (pd.DataFrame): Data of one or more sessions. Must contain ``SESSION_ID``,
            ``SCREEN_WIDTH``, ``SCREEN_HEIGHT`` and the coordinate columns.
        x_col (str): Name of the x coordinate column.
        y_col (str): Name of the y coordinate column.
        mode (str): ``"diagonal"`` (default) or ``"per_axis"``.
        unit (str): ``"normalized"`` (default) or ``"pixels"``.
        pixelsX (int): Reference width in pixels. Only used with ``unit="pixels"``.
        pixelsY (int): Reference height in pixels. Only used with ``unit="pixels"``.
        screen_size_source (str): How the screen size of each session is chosen.
            ``"mode"`` (default) uses the most frequent value. ``"first"`` uses the first
            valid value in row order, which is useful when the reported screen size changes
            with the browser zoom during the session (the first value is the one at the
            initial zoom). Sort the data by timestamp beforehand when using ``"first"``.

    Returns:
        pd.DataFrame: A copy of ``df`` with ``x_col`` and ``y_col`` replaced by the normalized values.

    Raises:
        ValueError: If ``mode``, ``unit`` or ``screen_size_source`` have an invalid value,
            if a required column is missing, or if any session has a missing or
            non-positive screen size.
    """
    validate_dataframe(df)
    if mode not in SCREEN_NORMALIZATION_MODES:
        raise ValueError(f"mode must be one of {SCREEN_NORMALIZATION_MODES}.")
    if unit not in SCREEN_NORMALIZATION_UNITS:
        raise ValueError(f"unit must be one of {SCREEN_NORMALIZATION_UNITS}.")
    if screen_size_source not in SCREEN_SIZE_SOURCES:
        raise ValueError(f"screen_size_source must be one of {SCREEN_SIZE_SOURCES}.")
    required_columns = {ColumnNames.SESSION_ID, ColumnNames.SCREEN_WIDTH, ColumnNames.SCREEN_HEIGHT, x_col, y_col}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing columns: {sorted(missing_columns)}")

    sessions = df.groupby(ColumnNames.SESSION_ID, sort=False, dropna=False)
    size_aggregation = _most_frequent if screen_size_source == "mode" else "first"
    screen_width = pd.to_numeric(sessions[ColumnNames.SCREEN_WIDTH].transform(size_aggregation), errors="coerce")
    screen_height = pd.to_numeric(sessions[ColumnNames.SCREEN_HEIGHT].transform(size_aggregation), errors="coerce")

    valid_screen = (screen_width > 0) & (screen_height > 0)          # False for missing/invalid sizes
    if not valid_screen.all():                                       # Fail loudly instead of producing NaN silently
        invalid_sessions = df.loc[~valid_screen, ColumnNames.SESSION_ID].unique().tolist()
        raise ValueError(f"Missing or invalid screen size in sessions: {invalid_sessions}. "
                         "Fix or remove them before normalizing.")

    if mode == "diagonal":                                           # One shared scale for both axes
        x_scale = y_scale = np.hypot(screen_width, screen_height)
        reference_x = reference_y = np.hypot(pixelsX, pixelsY) if unit == "pixels" else 1.0
    else:                                                            # Independent scale per axis
        x_scale, y_scale = screen_width, screen_height
        reference_x, reference_y = (pixelsX, pixelsY) if unit == "pixels" else (1.0, 1.0)

    x_factor = reference_x / x_scale
    y_factor = reference_y / y_scale

    has_valid_position = (df[x_col] > -1) & (df[y_col] > -1)         # Skip -1 sentinels
    normalized_trace = df.copy()                                     # Never modify the caller's data
    normalized_trace[x_col] = np.where(has_valid_position, df[x_col] * x_factor, df[x_col])
    normalized_trace[y_col] = np.where(has_valid_position, df[y_col] * y_factor, df[y_col])
    return normalized_trace