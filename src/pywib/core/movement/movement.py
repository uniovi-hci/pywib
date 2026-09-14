import pandas as pd

from pywib.utils import (acceleration_traces, velocity_traces, velocity_df, 
                         acceleration_df, jerkiness_df, jerkiness_traces, 
                         validate_dataframe, compute_metrics_from_traces, extract_traces_by_session)
from pywib.constants import ColumnNames
from pywib.utils.movement import velocity_traces_parallel
from pywib.utils.validation import validate_any_not_none

def _traces_missing_column(traces: dict[str, list[pd.DataFrame]] | None, column_name: str) -> bool:
    if traces is None:
        return False
    return any(
        column_name not in trace.columns
        for session_traces in traces.values()
        for trace in session_traces
    )

def velocity(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None, per_traces: bool = True, parallel:bool = False, n_jobs: int = 2) -> dict[str, list[pd.DataFrame]]:
    """
    Function to calculate velocity for either a single DataFrame or a traces dictionary.

    If `traces` is None, they will be computed from the DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'x', 'y', and 'timeStamp' columns.
        traces (dict[str, list[pd.DataFrame]]): Dictionary mapping session IDs to lists of DataFrames.
        per_traces (bool): Whether to compute velocity per trace. If False, compute directly on df.

    Returns:
        dict[str, list[pd.DataFrame]]: Dictionary of traces with computed 'velocity' column.
    """

    validate_any_not_none(df, traces)

    if not per_traces:
        # Compute directly on the DataFrame (no trace extraction)
        return velocity_df(df)

    # If traces are not provided, extract them from df
    if traces is None:
        validate_dataframe(df)
        traces = extract_traces_by_session(df)

    if parallel:
        # Compute velocity for each trace in parallel
        return velocity_traces_parallel(traces, n_jobs=n_jobs)

    # Compute velocity for each trace
    return velocity_traces(traces)


def velocity_metrics(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None) -> dict:
    """
    Calculate velocity metrics for the given DataFrame or traces.
    This function computes the mean, max, and min velocity for each session.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'velocity' column.
        traces (dict): A dictionary with keys as (sessionId) and values as lists of DataFrames. If None, traces will be computed from df.

    Returns:
        dict: A dictionary with keys as (sessionId) and values as dictionaries with 'mean ', 'max', and 'min' velocity.
    """
    
    validate_any_not_none(df, traces)

    if (df is not None) and (
        (ColumnNames.VELOCITY not in df.columns) or
        (traces is None) or
        _traces_missing_column(traces, ColumnNames.VELOCITY)
    ):
        validate_dataframe(df)
        traces = velocity(df, per_traces=True)

    return compute_metrics_from_traces(
        df=df,
        traces=traces,
        column_name=ColumnNames.VELOCITY,
        compute_traces_fn=lambda _: traces,
        preprocess_fn=lambda s: s[s > 0]  # Exclude zero velocities
    )

def acceleration(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None, per_traces: bool = True) -> dict[str, list[pd.DataFrame]]:
    """
    Wrapper function to calculate acceleration for either a single DataFrame or a traces dictionary.

    If `traces` is None, they will be computed from the DataFrame.
    """

    validate_any_not_none(df, traces)

    if not per_traces:
        # Compute directly on the DataFrame (no trace extraction)
        return acceleration_df(df)

    # If traces are not provided, extract them from df
    if traces is None:
        validate_dataframe(df)
        traces = extract_traces_by_session(df)

    # Compute acceleration for each trace
    return acceleration_traces(traces)

def acceleration_metrics(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None) -> dict:
    """
    Calculate acceleration metrics for the given DataFrame or traces.
    This function computes the mean, max, and min acceleration for each session.

    Parameters:
        df (pd.DataFrame): DataFrame containing interaction data. Optionally already including 'acceleration' column.
        traces (dict): A dictionary with keys as (sessionId) and values as lists of DataFrames. If None, traces will be computed from df.
    Returns:
        dict: A dictionary with keys as (sessionId) and values as dictionaries with 'mean', 'max', and 'min' acceleration.
    """

    
    validate_any_not_none(df, traces)

    if (df is not None) and (
        (ColumnNames.ACCELERATION not in df.columns) or
        (traces is None) or
        _traces_missing_column(traces, ColumnNames.ACCELERATION)
    ):
        validate_dataframe(df)
        if ColumnNames.VELOCITY not in df.columns:
            traces = velocity(df, per_traces=True)
        traces = acceleration(df, traces, per_traces=True)

    return compute_metrics_from_traces(
        df=df,
        traces=traces,
        column_name=ColumnNames.ACCELERATION,
        compute_traces_fn=lambda _: traces,  # Already computed above
        preprocess_fn=lambda s: s[s != 0]    # Exclude zero accelerations
    )

def jerkiness(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None, per_traces: bool = True) -> dict[str, list[pd.DataFrame]]:
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
   
    validate_any_not_none(df, traces)

    if not per_traces:
        # Compute directly on the DataFrame (no trace extraction)
        return jerkiness_df(df)

    # If traces are not provided, extract them from df
    if traces is None:
        validate_dataframe(df)
        traces = extract_traces_by_session(df)

    # Compute jerkiness for each trace
    return jerkiness_traces(traces)

def jerkiness_metrics(df: pd.DataFrame, traces: dict[str, list[pd.DataFrame]] = None) -> dict:
    """
    Calculate jerkiness metrics for the given DataFrame or traces.
    This function computes the mean, max, and min jerkiness for each session.

    Parameters:
        df (pd.DataFrame): DataFrame containing interaction data. Optionally already including 'jerkiness' column.
        traces (dict): A dictionary with keys as (sessionId) and values as lists of DataFrames. If None, traces will be computed from df.
    Returns:
        dict: A dictionary with keys as (sessionId) and values as dictionaries with 'mean', 'max', and 'min' jerkiness.
    """
    
    validate_any_not_none(df, traces)

    if (df is not None) and (
        (ColumnNames.JERKINESS not in df.columns) or
        (traces is None) or
        _traces_missing_column(traces, ColumnNames.JERKINESS)
    ):
        validate_dataframe(df)
        if ColumnNames.ACCELERATION not in df.columns:
            if ColumnNames.VELOCITY not in df.columns:
                traces = velocity(df, per_traces=True)
            traces = acceleration(df, traces, per_traces=True)
        traces = jerkiness(df, traces, per_traces=True)

    return compute_metrics_from_traces(
        df=df,
        traces=traces,
        column_name=ColumnNames.JERKINESS,
        compute_traces_fn=lambda _: traces,  # Already computed above
        preprocess_fn=lambda s: s[s != 0]    # Exclude zero jerkiness
    )

