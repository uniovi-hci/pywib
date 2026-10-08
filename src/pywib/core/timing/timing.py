import pandas as pd
from pywib.utils.validation import validate_any_not_none, validate_dataframe
from pywib.utils.segmentation import extract_traces_by_session
from pywib.utils.timing import num_pauses_df, num_pauses_traces, pauses_metrics_df, pauses_metrics_per_trace
from pywib.utils.utils import compute_space_time_diff
from pywib.utils.batch import concat_session, space_time_diff_grouped
from pywib.constants import ColumnNames

def execution_time(df: pd.DataFrame) -> dict:
    """
    Calculate the total execution time of a session in milliseconds, without taking pauses into account.
    This is the same as the total time from the first to the last event registered for the session.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'timeStamp' column.
    Returns:
        dict: Total execution time in milliseconds for each session.

    """
    validate_any_not_none(df)
    validate_dataframe(df)

    total_time_per_session = {}
    for session_id, session_df in df.groupby(ColumnNames.SESSION_ID):
        session_df = session_df.sort_values(by=ColumnNames.TIME_STAMP)
        total_time = session_df[ColumnNames.TIME_STAMP].iloc[-1] - session_df[ColumnNames.TIME_STAMP].iloc[0]
        total_time_per_session[session_id] = total_time
    return total_time_per_session

def movement_time(df: pd.DataFrame, traces: dict[str, list[pd.DataFrame]] = None) -> dict:
    """
    Calculate the total movement time from traces in milliseconds, taking pauses into account.
    This is the same as the interval of time the user is interacting with the interface.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing 'timeStamp' column.
        traces (dict): Dictionary with sessionId as keys and list of DataFrames as values.
    Returns:
        dict: A dictionary with sessionId as keys and total movement time in milliseconds as values.
    """
    
    validate_any_not_none(df, traces)

    if traces is None:
        validate_dataframe(df)
        traces = extract_traces_by_session(df)

    movement_time_per_session = {}
    for session_id, session_traces in traces.items():
        combined, sizes, ok = concat_session(session_traces)
        if combined is None:
            movement_time_per_session[session_id] = 0.0
            continue
        if ok:
            combined = space_time_diff_grouped(combined)
            movement_time_per_session[session_id] = float(
                combined[ColumnNames.DT].sum()
            )
            continue
        total_movement_time = 0.0
        for trace in session_traces:
            trace = compute_space_time_diff(trace)
            total_movement_time += trace[ColumnNames.DT].sum()
        movement_time_per_session[session_id] = total_movement_time

    return movement_time_per_session

def num_pauses(df: pd.DataFrame, traces:dict[str, list[pd.DataFrame]] = None, threshold: float = 100, computeTraces: bool = True) -> dict[str, dict]:
    """
    Calculate the number of pauses in the DataFrame.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing 'timeStamp' column.
        threshold (float): Time threshold in milliseconds to consider a pause, by default 100 ms.
        computeTraces (bool): Whether to compute traces by sessionId, by default True. If False, df is assumed to be already segmented by sessionId.
    
    Returns:
        dict: A dictionary containing the number of pauses and the mean pause pere trace.
        With :py:attr:`~pywib.constants.ColumnNames.NUMBER_OF_PAUSES` and :py:attr:`~pywib.constants.ColumnNames.MEAN_PAUSE_PER_TRACE` as keys.    
    """

    validate_any_not_none(df, traces)

    if computeTraces:
        if traces:
            return  num_pauses_traces(traces, threshold)
        else:
            validate_dataframe(df)
            return num_pauses_traces(extract_traces_by_session(df), threshold)
    else:
        validate_dataframe(df)
        return num_pauses_df(df, threshold)


def pauses_metrics(df: pd.DataFrame, threshold: float = 100, traces: dict[str, list[pd.DataFrame]] = None, per_traces = True) -> dict:
    """
    Calculate pause metrics for the given DataFrame.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing 'timeStamp' column.
        threshold (float): Time threshold in milliseconds to consider a pause, by default 100 ms.
        traces (dict): Dictionary with sessionId as keys and list of DataFrames as values.

    Returns:
        dict[str, dict]: A dictionary with sessionId as keys and a dictionary of pause metrics as values. These metrics are:
            - total_pauses: Total number of pauses
            - mean_pause_duration: Mean duration of the pauses
            - pause_duration (list[int]): An array of pauses durations
            - mean_pauses_per_trace: The mean number of pauses per trace
            - max_pause: The pause with maximum duration
            - min_pause: The pause with minimum duration 
    """

    validate_any_not_none(df, traces)
    
    if per_traces:
        if traces is None:
            validate_dataframe(df)
            traces = extract_traces_by_session(df)
        return pauses_metrics_per_trace(traces, threshold)
    else:
        validate_dataframe(df)
        return pauses_metrics_df(df, threshold)
    
    