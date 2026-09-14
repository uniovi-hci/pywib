import pandas as pd
import numpy as np
from pywib.constants import ColumnNames
from pywib.utils import validate_dataframe, compute_space_time_diff
from pywib.utils.utils import deprecated
from joblib import Parallel, delayed

def velocity_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate velocity for a single DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'x', 'y', and 'timeStamp' columns.

    Returns:
        pd.DataFrame: DataFrame with an additional 'velocity' column.
    """
    validate_dataframe(df)
    df = _path(df)  # Compute distance and dt first
    # Avoid division by zero if dt is 0
    df[ColumnNames.VELOCITY] = np.where(df[ColumnNames.DT] != 0, 
                                        df[ColumnNames.DISTANCE] / df[ColumnNames.DT], 
                                        0)
    return df


def velocity_traces(traces: dict[str, list[pd.DataFrame]]) -> dict[str, list[pd.DataFrame]]:
    """
    Calculate velocity for a dictionary of traces (each a list of DataFrames).

    Parameters:
        traces (dict[str, list[pd.DataFrame]]): Mapping of sessionId to list of DataFrames.

    Returns:
        dict[str, list[pd.DataFrame]]: Same structure, but with velocity computed in each DataFrame.
    """
    for session_id, session_traces in traces.items():
        for i, df in enumerate(session_traces):
            validate_dataframe(df)
            session_traces[i] = velocity_df(df)
        traces[session_id] = session_traces
    return traces

def velocity_traces_parallel(traces: dict[str, list[pd.DataFrame]], n_jobs: int = 2) -> dict[str, list[pd.DataFrame]]:
    """
    Calculate velocity for a dictionary of traces (each a list of DataFrames) in parallel.

    Parameters:
        traces (dict[str, list[pd.DataFrame]]): Mapping of sessionId to list of DataFrames.
        n_jobs (int): Number of parallel jobs.

    Returns:
        dict[str, list[pd.DataFrame]]: Same structure, but with velocity computed in each DataFrame.
    """

    def compute_velocity_for_trace(df):
        validate_dataframe(df)
        return velocity_df(df)

    for session_id, session_traces in traces.items():
        session_traces = Parallel(n_jobs=n_jobs)(
            delayed(compute_velocity_for_trace)(df) for df in session_traces
        )
        traces[session_id] = session_traces
    return traces

def acceleration_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate acceleration for a single DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'x', 'y', and 'timeStamp' columns.

    Returns:
        pd.DataFrame: DataFrame with an additional 'acceleration' column.
    """
    validate_dataframe(df)

    if(ColumnNames.VELOCITY not in df.columns):
        df = velocity_df(df)

    # Avoid division by zero if dt is 0
    df[ColumnNames.ACCELERATION] = np.where(df[ColumnNames.DT] != 0, 
                                            df[ColumnNames.VELOCITY].diff().fillna(0) / df[ColumnNames.DT], 
                                            0)
    return df


def acceleration_traces(traces: dict[str, list[pd.DataFrame]]) -> dict[str, list[pd.DataFrame]]:
    """
    Calculate acceleration for a dictionary of traces (each a list of DataFrames).

    Parameters:
        traces (dict[str, list[pd.DataFrame]]): Mapping of sessionId to list of DataFrames.

    Returns:
        dict[str, list[pd.DataFrame]]: Same structure, but with acceleration computed in each DataFrame.
    """
    for session_id, session_traces in traces.items():
        for i, df in enumerate(session_traces):
            validate_dataframe(df)
            session_traces[i] = acceleration_df(df)
        traces[session_id] = session_traces
    return traces

def jerkiness_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate jerkiness for a single DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'x', 'y', and 'timeStamp' columns.

    Returns:
        pd.DataFrame: DataFrame with an additional 'jerkiness' column.
    """
    validate_dataframe(df)

    if(ColumnNames.ACCELERATION not in df.columns):
        df = acceleration_df(df)

    # Avoid division by zero if dt is 0
    df[ColumnNames.JERKINESS] = np.where(df[ColumnNames.DT] != 0, 
                                         df[ColumnNames.ACCELERATION].diff().fillna(0) / df[ColumnNames.DT], 
                                         0)
    return df


def jerkiness_traces(traces: dict[str, list[pd.DataFrame]]) -> dict[str, list[pd.DataFrame]]:
    """
    Calculate jerkiness for a dictionary of traces (each a list of DataFrames).

    Parameters:
        traces (dict[str, list[pd.DataFrame]]): Mapping of sessionId to list of DataFrames.

    Returns:
        dict[str, list[pd.DataFrame]]: Same structure, but with jerkiness computed in each DataFrame.
    """
    for session_id, session_traces in traces.items():
        for i, df in enumerate(session_traces):
            validate_dataframe(df)
            session_traces[i] = jerkiness_df(df)
        traces[session_id] = session_traces
    return traces

@deprecated
def jerkiness(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None) -> dict[str, list[pd.DataFrame]]:
    """
    Compute jerkiness for either a single DataFrame or multiple traces.

    If `traces` is not provided, they are extracted from `df` using `extract_traces_by_session()`.

    Parameters
    ----------
    df : pd.DataFrame, optional
        DataFrame containing 'acceleration' and 'dt' columns.
    traces : dict[str, list[pd.DataFrame]], optional
        Dictionary mapping session IDs to lists of DataFrames.

    Returns
    -------
    dict[str, list[pd.DataFrame]]
        Dictionary of traces, each containing the computed 'jerkiness' column.
    """
    if traces is None:
        if df is None:
            raise ValueError("Either 'df' or 'traces' must be provided.")
        validate_dataframe(df)
        traces = extract_traces_by_session(df)
    return jerkiness_traces(traces)

def _path(trace: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function to calculate the path length for a single trace.
    This function computes the path length based on the Euclidean distance between consecutive points.

    Parameters:
        trace (pd.DataFrame): A single trace DataFrame.

    Returns:
        pd.DataFrame: DataFrame with an additional 'distance' column representing the path length.
    """

    if trace is None:
        raise ValueError("Trace DataFrame must be provided.")

    validate_dataframe(trace)

    trace = compute_space_time_diff(trace)
    trace[ColumnNames.DISTANCE] = np.sqrt(trace[ColumnNames.DX] ** 2 + trace[ColumnNames.DY] ** 2)

    return trace