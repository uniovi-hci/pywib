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

def find_zoom_bursts(trace_df: pd.DataFrame, max_gap_ms: int = 150):
    """Group wheel / scroll / resize / zoom-key events into bursts; keep bursts containing a resize."""
    key_direction = trace_df[ColumnNames.KEY_VALUE].astype(str).map(ZOOM_KEY_TO_DIRECTION)   # 'in'/'out'/'reset' or NaN
    is_zoom_key = trace_df[ColumnNames.EVENT_TYPE].isin(EventTypes.KEYBOARD_EVENTS_LIST) & key_direction.notna()  # Only zoom keys, not typing
    is_zoom_related = (trace_df[ColumnNames.EVENT_TYPE].isin(EventTypes.SCROLL_EVENTS_LIST + [EventTypes.EVENT_WINDOW_RESIZE])
                       | is_zoom_key)                      # Every event that can belong to a zoom
    zoom_related_events = trace_df[is_zoom_related]        # Mouse moves and other events are ignored here
    burst_id = (zoom_related_events[ColumnNames.TIME_STAMP].diff() > max_gap_ms).cumsum()  # New burst after a long gap
    bursts = [burst for _, burst in zoom_related_events.groupby(burst_id)
              if (burst[ColumnNames.EVENT_TYPE] == EventTypes.EVENT_WINDOW_RESIZE).any()]  # A zoom always emits a resize
    return bursts, key_direction

def find_anchor_events(trace_df, burst, has_position):
    """Positioned events to measure with: last one before the burst, those inside it, first one after it."""
    first_index, last_index = burst.index[0], burst.index[-1]                      # Row range of the burst
    before_burst = trace_df[has_position & (trace_df.index < first_index)].tail(1)  # Last known position before
    inside_burst = trace_df[has_position & (trace_df.index >= first_index) & (trace_df.index <= last_index)]
    after_burst = trace_df[has_position & (trace_df.index > last_index)].head(1)    # First known position after
    return pd.concat([before_burst, inside_burst, after_burst])                    # Already in row order


def normalize_coordinates_for_zoom(trace_df, browser_name="", max_gap_ms=150, log_tolerance=0.04,
                                   min_valid_x=100, initial_zoom_factor=1.0):
    zoom_levels = get_zoom_levels_for_browser(browser_name)                   # Zoom steps of this browser
    sorted_trace = trace_df.copy()
    sorted_trace[ColumnNames.TIME_STAMP] = pd.to_numeric(sorted_trace[ColumnNames.TIME_STAMP], errors="coerce")
    sorted_trace = sorted_trace.sort_values(ColumnNames.TIME_STAMP, kind="stable").reset_index(drop=True)
    x_positions = sorted_trace[ColumnNames.X].to_numpy(float)                         # pageX values
    has_position = (sorted_trace[ColumnNames.EVENT_TYPE].isin([EventTypes.EVENT_ON_MOUSE_MOVE, EventTypes.EVENT_ON_WHEEL])
                    & (sorted_trace[ColumnNames.X] > -1) & (sorted_trace[ColumnNames.Y] > -1))  # Events that carry a real position

    current_level_index = int(np.argmin(np.abs(zoom_levels - initial_zoom_factor)))  # Starting zoom level
    ratio_per_event = np.ones(len(sorted_trace))                              # Scale change at each row
    classification_per_event = np.full(len(sorted_trace), "", dtype=object)   # How each resize was resolved

    bursts, key_direction = find_zoom_bursts(sorted_trace, max_gap_ms)
    for burst in bursts:
        resize_indices = burst.index[burst[ColumnNames.EVENT_TYPE] == EventTypes.EVENT_WINDOW_RESIZE]  # Zoom steps in this burst
        burst_key_directions = key_direction[burst.index].dropna().tolist()         # Zoom keys pressed in the burst

        if len(burst_key_directions) == len(resize_indices):                  # One key per resize: steps are known
            for resize_index, direction in zip(resize_indices, burst_key_directions):
                candidates = list_possible_zoom_transitions(zoom_levels, current_level_index, direction, 1)
                resolution = choose_zoom_transition(candidates, np.nan, True, log_tolerance)
                if resolution is None:
                    classification_per_event[resize_index] = "unresolved"
                    continue
                current_level_index, ratio_per_event[resize_index], _ = resolution
                classification_per_event[resize_index] = "key"
            continue

        anchors = find_anchor_events(sorted_trace, burst, has_position)       # Positioned events around the burst
        resolved_resizes = set()                                              # Resizes covered by a measurement
        for anchor_before, anchor_after in zip(anchors.index[:-1], anchors.index[1:]):
            resizes_between = resize_indices[(resize_indices > anchor_before) & (resize_indices < anchor_after)]
            if len(resizes_between) == 0:                                     # No zoom step between these two
                continue
            if x_positions[anchor_before] < min_valid_x:                      # Near the left edge: ratio unreliable
                continue
            measured_ratio = x_positions[anchor_after] / x_positions[anchor_before]  # Old zoom / new zoom
            candidates = list_possible_zoom_transitions(
                zoom_levels, current_level_index, None, len(resizes_between)) # Net change of -k..k levels
            if len(resizes_between) >= 2:                                     # In + out cancel each other
                candidates.append((current_level_index, 1.0))
            resolution = choose_zoom_transition(candidates, measured_ratio, False, log_tolerance)
            if resolution is None:                                            # No step combination fits
                continue
            current_level_index, ratio_per_event[resizes_between[-1]], _ = resolution  # Whole change on last resize
            classification_per_event[resizes_between] = "measured"            # All steps of this span are resolved
            resolved_resizes.update(resizes_between)
        for resize_index in resize_indices:                                   # Anything not covered stays unknown
            if resize_index not in resolved_resizes:
                classification_per_event[resize_index] = "unresolved"

    sorted_trace["zoom_classification"] = classification_per_event
    sorted_trace["zoom_break"] = classification_per_event == "unresolved"     # Scale unknown from here on
    sorted_trace["cumulative_scale"] = np.cumprod(ratio_per_event)
    has_valid_position = (sorted_trace[ColumnNames.X] > -1) & (sorted_trace[ColumnNames.Y] > -1)
    sorted_trace["x_normalized"] = np.where(has_valid_position, sorted_trace[ColumnNames.X] / sorted_trace["cumulative_scale"], sorted_trace[ColumnNames.X])
    sorted_trace["y_normalized"] = np.where(has_valid_position, sorted_trace[ColumnNames.Y] / sorted_trace["cumulative_scale"], sorted_trace[ColumnNames.Y])
    return sorted_trace

def normalize_coordinates_for_screen_size(df: pd.DataFrame,
                                          x_col: str = ColumnNames.X,
                                          y_col: str = ColumnNames.Y,
                                          mode: str = "diagonal", type: str = "normalized", pixelsX: int = 1920, pixelsY: int = 1080) -> pd.DataFrame:
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
        # Multiply back by a pixelsX x pixelsY diagonal
        if mode == "per_axis":                                    # Independent scale per axis
            x_scale, y_scale = pixelsX, pixelsY
        elif mode == "diagonal":                                  # One shared scale for both axes
            x_scale = y_scale = np.hypot(pixelsX, pixelsY)        # Screen diagonal in px
        normalized_trace["x_screen_normalized"] = np.where(
            has_valid_position,
            normalized_trace["x_screen_normalized"] * x_scale,
            normalized_trace["x_screen_normalized"],
        )
        normalized_trace["y_screen_normalized"] = np.where(
            has_valid_position,
            normalized_trace["y_screen_normalized"] * y_scale,
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
    