import functools
from typing import Callable, ParamSpec, TypeVar
import warnings
import pandas as pd
from ..constants import ColumnNames
from ..utils.validation import validate_dataframe

def compute_space_time_diff(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute space and time differences (dx, dy, dt) for the given DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'x', 'y', and 'timeStamp' columns.
    
    Returns:
        pd.DataFrame: DataFrame with additional 'dx', 'dy', and 'dt' columns.
    """
    if(ColumnNames.X not in df.columns or
       ColumnNames.Y not in df.columns or
       ColumnNames.TIME_STAMP not in df.columns or
       ColumnNames.SESSION_ID not in df.columns):
        raise ValueError(f"DataFrame must contain '{ColumnNames.X}', '{ColumnNames.Y}', '{ColumnNames.TIME_STAMP}', and '{ColumnNames.SESSION_ID}' columns.")

    df = df.copy()
    df.sort_values(by=[ColumnNames.TIME_STAMP], inplace=True)
    df[ColumnNames.TIME_STAMP] = pd.to_numeric(df[ColumnNames.TIME_STAMP], errors='coerce')
    df[ColumnNames.DT] = df.groupby([ColumnNames.SESSION_ID])[ColumnNames.TIME_STAMP].diff().fillna(0)
    df[ColumnNames.DX] = df.groupby([ColumnNames.SESSION_ID])[ColumnNames.X].diff().fillna(0)
    df[ColumnNames.DY] = df.groupby([ColumnNames.SESSION_ID])[ColumnNames.Y].diff().fillna(0)
    return df

def compute_metrics_from_traces(
    df: pd.DataFrame,
    traces: dict[str, list[pd.DataFrame]] | None,
    column_name: str,
    compute_traces_fn,
    preprocess_fn=None,
) -> dict:
    """
    Compute basic statistical metrics (mean, max, min) for a specific column across sessions.

    This function serves as a generic helper for computing metrics such as velocity or acceleration
    over session-based trace data. It can automatically compute traces if they are not provided and
    allows for custom preprocessing (e.g., filtering out zero values).

    Parameters:
        df (pd.DataFrame): 
            A DataFrame containing the necessary data. Must include the specified column 
            or enough information to compute it via `compute_traces_fn`.

        traces (dict[str, list[pd.DataFrame]] | None): 
            Optional dictionary containing session traces. 
            Each key corresponds to a sessionId, and its value is a list of DataFrames 
            representing that session's traces. If None, traces will be computed using 
            `compute_traces_fn(df)`.

        column_name (str): 
            The name of the column from which to compute metrics (e.g., "velocity", "acceleration").

        compute_traces_fn (Callable): 
            A function that, given a DataFrame, computes and returns the corresponding traces dictionary.

        preprocess_fn (Callable | None): 
            Optional function applied to the concatenated column values before computing statistics. 
            Typically used to filter out zero or invalid values.

    Returns:
        dict:
            A dictionary where keys are sessionIds and values are dictionaries containing:
            - 'mean': Mean value.
            - 'max': Maximum value.
            - 'min': Minimum value.
    """
    if (traces is None):
        validate_dataframe(df)
        traces = compute_traces_fn(df, per_traces=True)

    metrics = {}
    for session_id, session_traces in traces.items():
        if(len(session_traces) > 0):
            for trace_index, trace in enumerate(session_traces):
                if column_name not in trace.columns:
                    raise ValueError(
                        f"Missing required column '{column_name}' in "
                        f"session '{session_id}', trace index {trace_index}."
                    )
            values = pd.concat([trace[column_name] for trace in session_traces])
            if preprocess_fn:
                values = preprocess_fn(values)
            metrics[session_id] = {
                'mean': values.mean(),
                'max': values.max(),
                'min': values.min()
            }

    return metrics

rT = TypeVar('rT') # return type
pT = ParamSpec('pT') # parameters type
def deprecated(func: Callable[pT, rT]) -> Callable[pT, rT]:
    """Use this decorator to mark functions as deprecated.
    Every time the decorated function runs, it will emit
    a "deprecation" warning."""
    @functools.wraps(func)
    def new_func(*args: pT.args, **kwargs: pT.kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to a deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    return new_func

def to_pywib_df(df: pd.DataFrame, colSessionId: str, colX: str, colY: str, colTimeStamp: str, colKeyValue: str = None, colKeyCode: str = None) -> pd.DataFrame:
    """
    Convert a DataFrame to the standard PyWib format.

    Parameters:
        df (pd.DataFrame): Input DataFrame with arbitrary column names.
        colSessionId (str): Name of the column representing the session ID.
        colX (str): Name of the column representing the X coordinate.
        colY (str): Name of the column representing the Y coordinate.
        colTimeStamp (str): Name of the column representing the timestamp.
        colKeyValue (str | None): Name of the column representing the key value.
        colKeyCode (str | None): Name of the column representing the key code.

    Returns:
        pd.DataFrame: A new DataFrame with standardized column names for PyWib.
    """

    if(df is None or df.empty):
        raise ValueError("Input DataFrame is empty or None.")

    if(colKeyValue is not None):
        df = df.rename(columns={colKeyValue: ColumnNames.KEY_VALUE})
    if(colKeyCode is not None):
        df = df.rename(columns={colKeyCode: ColumnNames.KEY_CODE})

    return df.rename(columns={
        colX: ColumnNames.X,
        colY: ColumnNames.Y,
        colTimeStamp: ColumnNames.TIME_STAMP,
        colSessionId: ColumnNames.SESSION_ID
    })