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

def get_zoom_levels_for_browser(browser_name: str) -> np.ndarray:
    """
    Return the list of discrete zoom levels for the given browser name.

    Parameters:
        browser_name (str): The browser name to get the zoom levels for. Case insensitive.
    """
    browser_name_lower = str(browser_name).lower()         
    for known_browser, zoom_levels in ZOOM_LEVELS_BY_BROWSER_NAME.items():  
        if known_browser in browser_name_lower:             
            return np.array(zoom_levels, float)             
    return np.array(CHROMIUM_ZOOM_LEVELS, float)            




def find_positions_around_resize(x_positions: list[int], resize_index: int, window_start_index: int,
                                 window_end_index: int, min_valid_x: int = 0):
    """
    Find the last valid x before the resize (old scale) and the first valid x after it (new scale).
    
    Parameters:
        x_positions (list[int]): The x positions of the session trace
        resize_index (int): The index in which the resize occurs
        window_start_index (int): ?
        window_end_index (int): ?
        min_valid_x (int): Minimum valid value for an x coordinate. Defaults to 0.
    """
    # Indices (relative to the window start) of events BEFORE the resize with a usable x
    valid_before = np.flatnonzero(x_positions[window_start_index:resize_index] >= min_valid_x)
    # Indices (relative to resize_index + 1) of events AFTER the resize with a usable x
    valid_after = np.flatnonzero(x_positions[resize_index + 1:window_end_index] >= min_valid_x)
    if len(valid_before) == 0 or len(valid_after) == 0:     # Nothing usable on at least one side
        return None                                         # Caller will treat the zoom as having no positions
    index_before_zoom = window_start_index + valid_before[-1]   # Closest valid event before (absolute index)
    index_after_zoom = resize_index + 1 + valid_after[0]        # Closest valid event after (absolute index)
    return index_before_zoom, index_after_zoom



def detect_zoom_events(df: pd.DataFrame, wheel_window_ms=100, key_window_ms=300, min_valid_x=100) -> list[dict]:
    """
    Find every resize caused by a zoom (wheel around it, or a zoom key just before it).

    Parameters:
        df (pd.DataFrame): DataFrame of the session in which the zoom levels will be detected
        wheel_window_ms (int): Threshold for a wheel resize event. Defaults to 100.
        key_window_ms (int): Threshold for a key window resize event. Defaults to 300.
        min_valid_x (int): Minimum valid value for an x coordinate. Defaults to 0.

    """
    event_types = df[ColumnNames.EVENT_TYPE]
    key_values =  df[ColumnNames.KEY_VALUE]
    timestamps = df[ColumnNames.TIME_STAMP]
    x_positions = df[ColumnNames.X]

    is_keyboard_event = np.isin(event_types, EventTypes.KEYBOARD_EVENTS_LIST)

    key_direction_per_event = [
        ZOOM_KEY_TO_DIRECTION.get(str(key_value)) if is_key else None
        for key_value, is_key in zip(key_values, is_keyboard_event)
    ]

    detected_zoom_events = []
    
    for resize_index in np.flatnonzero(event_types == EventTypes.EVENT_WINDOW_RESIZE):

        # First event inside the wheel window before the resize
        window_start_index = np.searchsorted(timestamps, timestamps[resize_index] - wheel_window_ms, "left")

        # One past the last event inside the wheel window after the resize
        window_end_index = np.searchsorted(timestamps, timestamps[resize_index] + wheel_window_ms, "right")

        # First event inside the (longer) key window before the resize
        key_window_start_index = np.searchsorted(timestamps, timestamps[resize_index] - key_window_ms, "left")

        # Zoom-key directions pressed shortly before the resize (None values dropped)
        recent_key_directions = [d for d in key_direction_per_event[key_window_start_index:resize_index] if d]
        key_direction = recent_key_directions[-1] if recent_key_directions else None

        # Wheel/scroll events on both sides of the resize within the window
        wheel_surrounds_resize = (
            np.isin(event_types[window_start_index:resize_index], EventTypes.SCROLL_EVENTS_LIST).any()
            and np.isin(event_types[resize_index + 1:window_end_index], EventTypes.SCROLL_EVENTS_LIST).any()
        )

        if key_direction is None and not wheel_surrounds_resize:  # Neither key nor wheel evidence
            continue                                         # Ordinary window resize: not a zoom

        positions_around = find_positions_around_resize(     # Look for measurable positions around the resize
            x_positions, resize_index, window_start_index, window_end_index, min_valid_x)
        
        index_before_zoom, index_after_zoom = positions_around if positions_around else (None, None)

        # Did the mouse move between the "before" and "after" events?
        mouse_moved_during_zoom = positions_around is not None and bool(
            (event_types[index_before_zoom:index_after_zoom + 1].isin(EventTypes.MOVE_EVENT_LIST)).any())
        
        detected_zoom_events.append(dict({
            'resize_index':resize_index,                       # Row of the resize event that anchors the zoom
            'window_start_index':window_start_index,           # Start of the time window before the resize
            'key_direction':key_direction,                     # 'in' / 'out' / 'reset' / None (wheel zoom)
            'index_before_zoom':index_before_zoom,             # Row measured at the old scale (or None)
            'index_after_zoom':index_after_zoom,               # Row measured at the new scale (or None)
            'mouse_moved_during_zoom':mouse_moved_during_zoom, # True if the mouse moved while zooming
        }))
    return detected_zoom_events


def estimate_zoom_ratio_mouse_still(x_positions: list[int], zoom_event) -> float:
    """
    Case 1 (mouse still): ratio = x after / x before = old zoom / new zoom. 
    Only x is used because pageY includes scroll.

    Parameters:
        x_positions (list[int]): List of x positions of the session
        zoom_event: List of ?
    """

    return x_positions[zoom_event["index_after_zoom"]] / x_positions[zoom_event["index_before_zoom"]]

def estimate_zoom_ratio_mouse_moving(event_types, timestamps, x_positions, zoom_event) -> float:
    """
    Case 2 (mouse moving): extrapolate the old x using recent mouse velocity, then compute the ratio.

    Paramters:  
        event_types:
        timestamps: 
        x_positions: 
        zoom_event:
    """

    index_before_zoom = zoom_event["index_before_zoom"]      # Row at the old scale
    index_after_zoom = zoom_event["index_after_zoom"]        # Row at the new scale
    expected_x_before_zoom = float(x_positions[index_before_zoom])  # Starting guess: last known x at old scale
    recent_mouse_move_indices = [                            # Valid mouse moves between window start and the "before" row
        row for row in range(zoom_event["window_start_index"], index_before_zoom + 1)
        if event_types[row].isin(EventTypes.MOVE_EVENT_LIST) and x_positions[row] >= 0
    ]
    if (len(recent_mouse_move_indices) >= 2                  # Need two moves to compute a velocity...
            and timestamps[recent_mouse_move_indices[-1]] > timestamps[recent_mouse_move_indices[-2]]):  # ...with distinct times
        last_move, previous_move = recent_mouse_move_indices[-1], recent_mouse_move_indices[-2]
        x_velocity_px_per_ms = ((x_positions[last_move] - x_positions[previous_move])
                                / (timestamps[last_move] - timestamps[previous_move]))  # Speed in the old scale
        elapsed_ms = timestamps[index_after_zoom] - timestamps[index_before_zoom]       # Time between both measurements
        expected_x_before_zoom += x_velocity_px_per_ms * elapsed_ms  # Where x would be now if the old scale still applied
    if expected_x_before_zoom <= 0:                          # Avoid dividing by zero or a negative position
        return np.nan                                        # Ratio cannot be estimated
    return x_positions[index_after_zoom] / expected_x_before_zoom  # Measured new x / expected old x

def list_possible_zoom_transitions(zoom_levels, current_level_index, key_direction, max_level_jump):
    """
    Return candidate (new_level_index, ratio) pairs, where ratio = old zoom / new zoom.
    
    Parameters:
        zoom_levels:
        current_level_index:
        key_direction:
        max_level_jump:
    """

    if key_direction == "reset":                             # Ctrl+0: go back to 100%
        reset_level_index = int(np.argmin(np.abs(zoom_levels - 1)))  # Index of the level closest to 1.0
        if reset_level_index != current_level_index:         # Only a transition if the level actually changes
            return [(reset_level_index, zoom_levels[current_level_index] / zoom_levels[reset_level_index])]
        return []                                            # Already at 100%: no transition
    if key_direction in ("in", "out"):                       # Key zoom: exactly one step in a known direction
        level_offsets = [1 if key_direction == "in" else -1]
    else:                                                    # Wheel zoom: direction unknown, try nearby steps
        level_offsets = [k for k in range(-max_level_jump, max_level_jump + 1) if k]  # -2,-1,1,2 (skip 0)
    return [
        (current_level_index + offset,                       # Candidate new level index
         zoom_levels[current_level_index] / zoom_levels[current_level_index + offset])  # Its old/new zoom ratio
        for offset in level_offsets
        if 0 <= current_level_index + offset < len(zoom_levels)  # Discard levels outside the list
    ]


def choose_zoom_transition(candidate_transitions, measured_ratio, direction_known_from_key, log_tolerance):
    """
    Pick the transition to apply. Returns (new_level_index, ratio, key_ratio_mismatch) or None if unresolved.

    Parameters:
        candidate_transitions:
        measured_ratio:
        direction_known_from_key:
        log_tolerance:
    """

    if not candidate_transitions:                            # No possible transition
        return None
    if direction_known_from_key:                             # Key zoom: the step is unique
        new_level_index, expected_ratio = candidate_transitions[0]
        key_ratio_mismatch = bool(                           # Flag if the measured ratio disagrees with the expected one
            np.isfinite(measured_ratio)
            and abs(np.log(measured_ratio / expected_ratio)) > log_tolerance)
        return new_level_index, expected_ratio, key_ratio_mismatch
    if not np.isfinite(measured_ratio) or measured_ratio <= 0:  # Wheel zoom needs a valid measurement
        return None
    new_level_index, closest_ratio = min(                    # Candidate whose ratio is closest to the measured one
        candidate_transitions, key=lambda c: abs(np.log(measured_ratio / c[1])))
    if abs(np.log(measured_ratio / closest_ratio)) <= log_tolerance:  # Close enough to a real zoom step
        return new_level_index, closest_ratio, False
    return None


def normalize_coordinates_for_zoom(df: pd.DataFrame, browser_name: str = "",
                                   wheel_window_ms=100, key_window_ms=300,
                                   log_tolerance=0.04, min_valid_x=100,
                                   max_level_jump=2, initial_zoom_factor=1.0) -> pd.DataFrame:
    """
    Add cumulative zoom scale and zoom-normalized coordinates to the trace.
    
    Parameters:
        df (pd.DataFrame): The trace to normalize
        browser_name (str?): The name of the browser used by the user (if known).
    """

    zoom_levels = get_zoom_levels_for_browser(browser_name)
    
    sorted_df = df.copy()
    sorted_df[ColumnNames.TIME_STAMP] = pd.to_numeric(sorted_df[ColumnNames.TIME_STAMP], errors="coerce")
    sorted_df = sorted_df.sort_values(ColumnNames.TIME_STAMP, kind="stable").reset_index(drop=True)

    event_types = sorted_df[ColumnNames.EVENT_TYPE].to_numpy()
    timestamps = sorted_df[ColumnNames.TIME_STAMP].to_numpy(float)
    x_positions = sorted_df[ColumnNames.X].to_numpy(float)

    current_level_index = int(np.argmin(np.abs(zoom_levels - initial_zoom_factor)))  # Session's starting zoom level
    ratio_per_event = np.ones(len(sorted_df))             # Scale change at each event (1 = no change)
    classification_per_event = np.full(len(sorted_df), "", dtype=object)  # Label of how each zoom was handled

    for zoom_event in detect_zoom_events(sorted_df, wheel_window_ms, key_window_ms, min_valid_x):
        
        resize_index = zoom_event["resize_index"]            # Row where the ratio will be stored

        has_positions = zoom_event["index_before_zoom"] is not None  # Were positions available around the zoom?
        measured_ratio = np.nan

        if has_positions:
            if zoom_event["mouse_moved_during_zoom"]:        # Mouse moved: use the extrapolating estimator
                measured_ratio = estimate_zoom_ratio_mouse_moving(event_types, timestamps, x_positions, zoom_event)
            else:                                            # Mouse still: use the simple estimator
                measured_ratio = estimate_zoom_ratio_mouse_still(x_positions, zoom_event)

        if has_positions:                                    # Label the zoom by how it was measured
            zoom_label = "moving" if zoom_event["mouse_moved_during_zoom"] else "static"
        else:
            zoom_label = "inferred"                          # No positions: ratio comes from the tracked level only

        resolution = choose_zoom_transition(list_possible_zoom_transitions(zoom_levels, current_level_index, zoom_event["key_direction"], max_level_jump), measured_ratio, zoom_event["key_direction"] is not None, log_tolerance)
        
        if resolution is None:                               # Could not determine the step
            classification_per_event[resize_index] = "unresolved"
            continue

        current_level_index, ratio_per_event[resize_index], key_ratio_mismatch = resolution

        classification_per_event[resize_index] = zoom_label + ("_mismatch" if key_ratio_mismatch else "")

    sorted_df["zoom_classification"] = classification_per_event  # How each zoom was resolved
    sorted_df["cumulative_scale"] = np.cumprod(ratio_per_event)  # Initial zoom / current zoom at each event
    has_valid_position = (sorted_df[ColumnNames.X] > -1) & (sorted_df[ColumnNames.Y] > -1)  # Exclude the -1 sentinel values
    
    # Scale X and Y
    sorted_df[ColumnNames.X] = np.where(                 # Divide valid x by the scale; keep sentinels unchanged
        has_valid_position, sorted_df[ColumnNames.X] / sorted_df["cumulative_scale"], sorted_df[ColumnNames.X])
    sorted_df[ColumnNames.Y] = np.where(                 # Same for y
        has_valid_position, sorted_df[ColumnNames.Y] / sorted_df["cumulative_scale"], sorted_df[ColumnNames.Y])

    # Drop all columns that were not in the original DF
    
    return sorted_df


def normalize_coordinates_for_screen_size(df: pd.DataFrame,
                                          x_col: str = ColumnNames.X,
                                          y_col: str = ColumnNames.Y,
                                          mode: str = "diagonal", type: str = "normalized") -> pd.DataFrame:
    """
    Add screen-size-normalized coordinates to ONE session's trace in the range 0 to 1.

    mode="per_axis": x / screen_width, y / screen_height  -> use for positions, heatmaps, regions.
    mode="diagonal": x / diagonal, y / diagonal           -> use for distances (keeps the aspect ratio).
    """
    
    if(ColumnNames.SCREEN_WIDTH not in df.columns or ColumnNames.SCREEN_HEIGHT not in df.columns):
        raise ValueError(f"Columns {ColumnNames.SCREEN_WIDTH} and {ColumnNames.SCREEN_HEIGHT} must be in the DataFrame")
    normalized_trace = df.copy()                                   # Never modify the caller's data

    # The screen should not change within a session, so take the most frequent value
    screen_width = normalized_trace[ColumnNames.SCREEN_WIDTH].mode()[0]      # Typical screen width in px
    screen_height = normalized_trace[ColumnNames.SCREEN_HEIGHT].mode()[0]    # Typical screen height in px

    if not (screen_width > 0 and screen_height > 0):                     # Missing or invalid screen size
        normalized_trace["x_screen_normalized"] = np.nan                 # Cannot normalize: mark as missing
        normalized_trace["y_screen_normalized"] = np.nan
        return normalized_trace

    if mode == "per_axis":                                               # Independent scale per axis
        x_scale, y_scale = screen_width, screen_height
    elif mode == "diagonal":                                             # One shared scale for both axes
        x_scale = y_scale = np.hypot(screen_width, screen_height)        # Screen diagonal in px
    else:
        raise ValueError("mode must be 'per_axis' or 'diagonal'.")

    has_valid_position = (normalized_trace[x_col] > -1) & (normalized_trace[y_col] > -1)  # Skip -1 sentinels

    normalized_trace["x_screen_normalized"] = np.where(                  # Scale valid x, keep sentinels as they are
        has_valid_position, normalized_trace[x_col] / x_scale, normalized_trace[x_col])
    normalized_trace["y_screen_normalized"] = np.where(                  # Same for y
        has_valid_position, normalized_trace[y_col] / y_scale, normalized_trace[y_col])

    if type == "normalized":
        pass
    elif type == "pixels":
        # Multiply back by a 1920x1080 diagonal
        reference_diagonal = np.hypot(1920, 1080)
        normalized_trace["x_screen_normalized"] = np.where(
            has_valid_position,
            normalized_trace["x_screen_normalized"] * reference_diagonal,
            normalized_trace["x_screen_normalized"],
        )
        normalized_trace["y_screen_normalized"] = np.where(
            has_valid_position,
            normalized_trace["y_screen_normalized"] * reference_diagonal,
            normalized_trace["y_screen_normalized"],
        )
    
    normalized_trace[x_col] = normalized_trace["x_screen_normalized"]
    normalized_trace[y_col] = normalized_trace["y_screen_normalized"]

    return normalized_trace.drop(columns=["x_screen_normalized", "y_screen_normalized"])

def normalize_coordinates_to_screen(df: pd.DataFrame, x_col: str, y_col: str,
                                    mode: str = "diagonal", type: str = "normalized") -> pd.DataFrame:
    """Apply screen-size normalization independently to each session."""

    validate_dataframe(df)

    return df.groupby(
        ColumnNames.SESSION_ID,
        sort=False,
        group_keys=False,
    ).apply(
        lambda session_df: normalize_coordinates_for_screen_size(
            session_df,
            x_col=x_col,
            y_col=y_col,
            mode=mode,
            type=type
        ).assign(**{ColumnNames.SESSION_ID: session_df.name}),
    )
    