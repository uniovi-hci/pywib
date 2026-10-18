"""
Analysis module for HCI Web Interaction Analyzer

This module provides methods to analyze interaction data from DataFrames.
"""

import pandas as pd
import numpy as np
from pywib.utils.segmentation import extract_keystroke_traces_by_session
from pywib.utils import validate_dataframe_keyboard
from pywib.constants import EventTypes, ColumnNames
from pywib.utils.keyboard import (backspace_usage_df, backspace_usage_traces, typing_durations_df, typing_durations_traces, typing_speed_df, typing_speed_traces, word_per_minute)
from pywib.utils.validation import validate_any_not_none

def typing_durations(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None, per_traces: bool = True, single: bool = False) -> list:
    """
    Calculate the durations of individual keystrokes.

    Parameters:
        df (pd.DataFrame): DataFrame containing interaction data with 'event_type', 'timestamp', and 'key' columns.
        traces (dict[str, list[pd.DataFrame]]): optional Pre-extracted keystroke traces by session.
        per_traces (bool): optional whether to calculate durations per trace. Default is True.
        single (bool): optional, wether to compute durations fully (all the time the user is typing) or for every single keystroke (value for every single key press and release combination)
    Returns:
        list[float]: List of keystroke durations in milliseconds.
    """
    
    validate_any_not_none(df, traces)
    
    if traces is None and per_traces:
        validate_dataframe_keyboard(df)
        traces = extract_keystroke_traces_by_session(df)
        return typing_durations_traces(traces, False, single=single)

    if not per_traces:
        validate_dataframe_keyboard(df)
        return typing_durations_df(df)

    return typing_durations_traces(traces, single=single)

def typing_speed(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None, per_traces : bool = True) -> dict[list[float]] | float:
    """
    Calculate the average typing speed in characters per minute (CPM).

    Parameters:
        df (pd.DataFrame): DataFrame containing interaction data with 'event_type', 'timestamp', and 'key' columns.
        traces (dict[str, list[pd.DataFrame]]): optional Pre-extracted keystroke traces by session.
        per_traces (bool): optional Whether to calculate speed per trace. Default is True. if False, mind that the df must only contain typing data in order to obtain the correct CPM calculation.

    Returns:
        dict (dict[list[float]] | float) : A dictionary with session IDs as keys and lists of typing speeds (CPM) per trace as values, or a float representing the typing speed if per_traces is False.
    """

    validate_any_not_none(df, traces)

    if per_traces and traces is None:
        validate_dataframe_keyboard(df)
        traces = extract_keystroke_traces_by_session(df)
        return typing_speed_traces(traces, False)

    elif not per_traces:
        validate_dataframe_keyboard(df)
        return typing_speed_df(df)

    return typing_speed_traces(traces)

def typing_speed_metrics(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None) -> dict:
    """
    Calculate typing speed metrics including average CPM, total characters typed, and total time spent typing.
    
    This metrics include average typing speed (average_typing_speed) in CPM, total characters typed (total_characters), and total time spent typing (total_time_seconds) in seconds.
    
    The average keydown to keyup duration (avg_keydown_to_keyup_duration) is the average duration of a keystroke (from keydown to keyup) in milliseconds.

    Parameters:
        df : pd.DataFrame DataFrame containing interaction data with 'event_type', 'timestamp', and 'key' columns.
        traces : dict[str, list[pd.DataFrame]], optional Pre-extracted keystroke traces by session.
        per_trace : bool, optional Whether to calculate metrics per trace. Default is True.
    Returns:
        dict: A dictionary with session IDs as keys and their corresponding typing speed metrics as values.
        """
    
    validate_any_not_none(df, traces)

    if traces is None:
        traces = extract_keystroke_traces_by_session(df)
    
    session_speeds = typing_speed(None, traces=traces, per_traces=True)

    metrics_by_session = {}
    for session_id, speeds in session_speeds.items():
        if speeds:
            avg_speed = np.mean(speeds)
            total_chars = sum(session_traces[session_traces[ColumnNames.EVENT_TYPE] == EventTypes.EVENT_KEY_UP][ColumnNames.EVENT_TYPE].count() for session_traces in traces[session_id])
            total_time = sum((session_traces[ColumnNames.TIME_STAMP].diff().fillna(0).sum() / 1000.0) for session_traces in traces[session_id])
            avg_keydown_to_keyup_duration = np.mean([
                (trace[trace[ColumnNames.EVENT_TYPE] == EventTypes.EVENT_KEY_UP][ColumnNames.TIME_STAMP].values - trace[trace[ColumnNames.EVENT_TYPE] == EventTypes.EVENT_KEY_DOWN][ColumnNames.TIME_STAMP].values).mean()
                for trace in traces[session_id]
            ])
            metrics_by_session[session_id] = {
                "average_typing_speed": avg_speed,
                ColumnNames.TOTAL_CHARS: total_chars,
                "total_time_seconds": total_time,
                "avg_keydown_to_keyup_duration": avg_keydown_to_keyup_duration  # TODO Review
            }
    return metrics_by_session


def backspace_usage(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None, per_trace: bool = True) -> dict:
    """
    Calculate the backspace usage rate (backspaces per 100 characters typed) for each session.

    Parameters:
        df (pd.DataFrame): DataFrame containing interaction data with 'event_type', 'timestamp', and 'key' columns.
        traces (dict[str, list[pd.DataFrame]]): optional Pre-extracted keystroke traces by session.
        per_trace (bool): optional Whether to calculate usage per trace. Default is True.
    Returns:
        dict: A dictionary with session IDs as keys and their corresponding backspace counts as values.
    """
    
    validate_any_not_none(df, traces)

    if traces is None and per_trace:
        validate_dataframe_keyboard(df)
        traces = extract_keystroke_traces_by_session(df)
        return backspace_usage_traces(traces, False)
    if not per_trace:
        validate_dataframe_keyboard(df)
        return backspace_usage_df(df)
    
    return backspace_usage_traces(traces)

def words_per_minute(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None, per_traces : bool = True) -> dict[list[float]] | float:
    """
    Calculate the average typing speed in words per minute (WPM).

    Parameters:
        df (pd.DataFrame): DataFrame containing interaction data with 'event_type', 'timestamp', and 'key' columns.
        traces (dict[str, list[pd.DataFrame]]): optional Pre-extracted keystroke traces by session.
        per_traces (bool): optional Whether to calculate speed per trace. Default is True. if False, mind that the df must only contain typing data in order to obtain the correct CPM calculation.

    Returns:
        dict (dict[list[float]] | float) : A dictionary with session IDs as keys and lists of typing speeds (CPM) per trace as values, or a float representing the typing speed if per_traces is False.
    """

    validate_any_not_none(df, traces)

    if per_traces and traces is None:
        validate_dataframe_keyboard(df)
        traces = extract_keystroke_traces_by_session(df)
        return typing_speed_traces(traces, False)

    elif not per_traces:
        validate_dataframe_keyboard(df)
        return word_per_minute(df)

    # TODO create for traces
    return word_per_minute(traces)