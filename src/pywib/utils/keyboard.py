
import pandas as pd
from pywib.constants import ColumnNames, EventTypes, KeyValues
from pywib.utils.validation import validate_dataframe_keyboard 
from pywib.utils.segmentation import extract_keystroke_traces


def _typing_durations_full(df: pd.DataFrame) -> float:
    """
    Helper method that computes the typing duration of an **already pre-segmentedd** keystorke trace, returning the time in ms.
    Parameters:
        df: The DataFrame of the precomputed trace
    Returns:
        float: The time in ms of the typing trace
    """
    return df[ColumnNames.TIME_STAMP].iloc[-1] - df[ColumnNames.TIME_STAMP].iloc[0]

def _typing_durations_per_key(df: pd.DataFrame) -> list[float]:
    """
    Similar to _typing_durations_full, but this method computes the duration of **every single key**.
    Meaning that, if the user pressed "aaaabbb" you would get [4,2] if each press lasted 1ms.
    Parameters:
        df: The DataFrame of the precomputed trace
    Returns:
        list[float]: The times in ms of the typing trace
    """
    durations = []
    current_key = -1
    time_start = 0.0
    for _, event in df.iterrows():
        if(current_key != event[ColumnNames.KEY_VALUE]):
            current_key = event[ColumnNames.KEY_VALUE]
            time_start = event[ColumnNames.TIME_STAMP]
        else:
            if(event[ColumnNames.EVENT_TYPE] == EventTypes.EVENT_KEY_UP):
                durations.append(event[ColumnNames.TIME_STAMP] - time_start)
    return durations


def typing_durations_df(df: pd.DataFrame = None, validate: bool = True, single:bool=False) -> list:
    """
    Calculate the durations of individual keystrokes from a DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame containing interaction data with 'event_type', 'timestamp and 'key' columns.
        validate (bool): Whether to validate the input DataFrame. Default is True.
        single (bool): Wether to compute per single key press or by full keystroke interaction.
    Returns:
        list: List of keystroke durations in milliseconds.
    """
    if validate:
        validate_dataframe_keyboard(df)
    durations = []
    traces = extract_keystroke_traces(df)
    
    for trace in traces:
        if single:
            durations.append(_typing_durations_per_key(trace))
        else:
            durations += _typing_durations_full(trace)
    return durations

def typing_durations_traces(traces: dict[str, list[pd.DataFrame]], validate: bool = True, single: bool = False) -> dict[str, list[pd.DataFrame]]:
    """
    Calculate the durations of individual keystrokes from pre-extracted keystroke traces.

    Parameters:
        traces (dict[str, list[pd.DataFrame]]): Pre-extracted keystroke traces by session.
        validate (bool): Whether to validate the input DataFrames. Default is True.
        single (bool): Wether to compute per single key press or by full keystroke interaction.
    Returns:
        dict (dict[str, list[number]]): A dictionary with session IDs as keys and lists of keystroke durations per trace as values.
    """
    durations_per_session = {}
    for session_id, keystroke_traces in traces.items():
        durations = []
        for trace in keystroke_traces:
            validate_dataframe_keyboard(trace)
            if single:
                durations.append(_typing_durations_full(trace))
            else:
                durations += _typing_durations_full(trace)
        durations_per_session[session_id] = durations
    return durations_per_session

def typing_speed_df(df: pd.DataFrame = None, validate: bool = True) -> float:
    """
    Calculate the average typing speed in characters per minute (CPM) from a DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame containing interaction data with 'event_type', 'timestamp', and 'key' columns.
        validate (bool): Whether to validate the input DataFrame. Default is True.
    Returns:
        float: Average typing speed in characters per minute (CPM).
    """
    
    if validate:
        validate_dataframe_keyboard(df)

    traces = extract_keystroke_traces(df)
    total_chars, total_time = get_total_chars_and_time_traces(traces)
    if total_time > 0 :
        return total_chars / (total_time / 60)
    else:
        return 0.0

def typing_speed_traces(traces: dict[str, list[pd.DataFrame]], validate: bool = True) -> dict[str, list[float]]:
    """
    Calculate the average typing speed in characters per minute (CPM) from pre-extracted keystroke traces.

    Parameters:
        traces (dict[str, list[pd.DataFrame]]): Pre-extracted keystroke traces by session.
        validate (bool): Whether to validate the input DataFrames. Default is True.
    Returns:
        dict (dict[str, list[float]]): A dictionary with session IDs as keys and lists of typing speeds (CPM) per trace as values.
    """
    speed_by_session = {}
    for session_id, keystroke_traces in traces.items():
        speed_by_trace = []
        for trace in keystroke_traces:
            validate_dataframe_keyboard(trace)
            cpm = typing_speed_df(trace, validate)
            speed_by_trace.append(cpm)
        speed_by_session[session_id] = speed_by_trace
    return speed_by_session

def backspace_usage_df(df: pd.DataFrame = None, validate: bool = True) -> float:
    """
    Calculate the backspace usage rate as a percentage of total keystrokes from a DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame containing interaction data with 'event_type', 'timestamp', and 'key' columns.
        validate (bool): Whether to validate the input DataFrame. Default is True.
    Returns:
        float: Backspace usage rate as a percentage of total keystrokes.
    """
    if validate:
        validate_dataframe_keyboard(df)
    mask = (df[ColumnNames.EVENT_TYPE] == EventTypes.EVENT_KEY_DOWN) & ( (df[ColumnNames.KEY_VALUE] == KeyValues.KEY_VALUE_BACKSPACE) | (df[ColumnNames.KEY_VALUE] == KeyValues.KEY_VALUE_DELETE))

    return int(mask.sum())

def backspace_usage_traces(traces: dict[str, list[pd.DataFrame]], validate: bool = True) -> dict[str, list[float]]:
    """
    Calculate the backspace usage rate as a percentage of total keystrokes from pre-extracted keystroke traces.

    Parameters:
        traces (dict[str, list[pd.DataFrame]]): Pre-extracted keystroke traces by session.
        validate (bool): Whether to validate the input DataFrames. Default is True.
    Returns:
        dict (dict[str, list[float]]): A dictionary with session IDs as keys and lists of backspace usage rates per trace as values.
    """
    usage_by_session = {}
    for session_id, keystroke_traces in traces.items():
        backspace_count = 0
        for trace in keystroke_traces:
            validate_dataframe_keyboard(trace)
            usage = backspace_usage_df(trace, validate)
            backspace_count += usage
        usage_by_session[session_id] = backspace_count
    return usage_by_session

def word_per_minute(df: pd.DataFrame, word_size : int = 5) -> float:
    """
    Computes the number of words typed per minute using a word size.
    If not specified, the default word size is 5.

    Parameters:
        df (pd.DataFrame): DataFrame from which to compute the WPM
        word_size (int?): Word size, by default 5.
    """
    traces = extract_keystroke_traces(df)
    total_chars, total_time = get_total_chars_and_time_traces(traces)
    if total_time > 0 :
        return (total_chars/ word_size) / (total_time / 60)
    else:
        return 0.0
    
def word_per_minute_traces(traces: dict[str, list[pd.DataFrame]], word_size: int = 5) -> dict[str, list[float]]:
    """
    Computes the number of words typed per minute in a trace using a word size.
        If not specified, the default word size is 5.

        
    Parameters:
        traces (dict[str, list[pd.DataFrame]]): Traces for which to compute the WPM
        word_size (int?): Word size, by default 5.
    """

    return {
        session_id: [word_per_minute(trace, word_size) for trace in session_traces]
        for session_id, session_traces in traces.items()
    }


def typing_speed_words_traces(traces: dict[str, list[pd.DataFrame]], validate: bool = True) -> dict[str, list[float]]:
    """
    Calculate the average typing speed in characters per minute (CPM) from pre-extracted keystroke traces.

    Parameters:
        traces (dict[str, list[pd.DataFrame]]): Pre-extracted keystroke traces by session.
        validate (bool): Whether to validate the input DataFrames. Default is True.
    Returns:
        dict (dict[str, list[float]]): A dictionary with session IDs as keys and lists of typing speeds (CPM) per trace as values.
    """
    speed_by_session = {}
    for session_id, keystroke_traces in traces.items():
        speed_by_trace = []
        for trace in keystroke_traces:
            validate_dataframe_keyboard(trace)
            cpm = typing_speed_df(trace, validate)
            speed_by_trace.append(cpm)
        speed_by_session[session_id] = speed_by_trace
    return speed_by_session

def get_total_chars_and_time(df: pd.DataFrame):
    total_chars = 0
    total_time = 0.0
    keys = df[df[ColumnNames.EVENT_TYPE] == EventTypes.EVENT_KEY_DOWN]

    if keys.empty:
        return 0, 0.0

    time_start = df[ColumnNames.TIME_STAMP].iloc[0]
    time_end = df[ColumnNames.TIME_STAMP].iloc[-1]
    
    partial_time = (time_end - time_start) / 1000.0

    if partial_time <= 0:
        return 0, 0.0

    total_chars = len(keys)
    total_time = partial_time

    return total_chars, total_time

def get_total_chars_and_time_traces(traces: dict[str, list[pd.DataFrame]]) -> tuple[int, float]:
    total_chars = total_time = 0.0
    for trace in traces:
        chars, time  = get_total_chars_and_time(trace)
        total_time += time
        total_chars += chars
    if total_time > 0 :
        return total_chars, total_time
    else:
        return 0, 0.0