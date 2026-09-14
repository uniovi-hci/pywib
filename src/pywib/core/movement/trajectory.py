import pandas as pd
import numpy as np

from pywib.utils import (_path, validate_dataframe, compute_space_time_diff, 
                         extract_traces_by_session, 
                         auc_ratio_traces)
from pywib.constants import ColumnNames
from pywib.utils.movement import (auc_df, auc_traces, flips, _apply_metric_to_traces,
                                   _compute_angles, angular_acceleration_df, angular_velocity_df)
from pywib.utils.utils import deprecated
from pywib.utils.validation import validate_any_not_none

def path(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None) -> pd.DataFrame:
    """
    Calculate the path length for the given DataFrame.
    This function computes the path length based on the Euclidean distance between consecutive points.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'x' and 'y' columns.
        traces (dict): A dictionary with keys as (sessionId) and values as lists of DataFrames. If None, traces will be computed from df.

    Returns:
        pd.DataFrame: DataFrame with an additional 'distance' column representing the path length.
    """
    
    validate_any_not_none(df, traces)

    if traces is None:
        validate_dataframe(df)
        traces = extract_traces_by_session(df)

    for session_id, session_traces in traces.items():
            for i in range(len(session_traces)):
                validate_dataframe(session_traces[i])

            # Compute the distance for each trace
            for j in range(len(session_traces)):
                session_traces[j][ColumnNames.DISTANCE] = _path(session_traces[j])[ColumnNames.DISTANCE]
            
            # Store the traces with distance in the dictionary
            traces[session_id] = session_traces

    return traces


def auc(df: pd.DataFrame, traces: dict[str, list[pd.DataFrame]] = None, per_traces: bool = True) -> tuple| dict:
    """
    Calculate the Area Under the Curve (AUC) for the given DataFrame.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing 'timeStamp' and 'y' columns.
        traces (dict): A dictionary with keys as (sessionId) and values as lists of DataFrames. If None, traces will be computed from df.
        per_traces (bool): Whether to compute traces by sessionId, by default True.
    
    Returns:
        tuple: A tuple (Geometric Auc, Execution Auc) as values if not per traces.
        dict: Dictionary sessionId as keys and a list with a tuple (Geometric Auc, Execution Auc) as values if per traces.
    """
    validate_any_not_none(df, traces)

    if not per_traces:
        # Compute directly on the DataFrame (no trace extraction)
        return auc_df(df)

    # If traces are not provided, extract them from df
    if traces is None:
        validate_dataframe(df)
        traces = extract_traces_by_session(df)

    # Compute auc for each trace
    return auc_traces(traces)


@deprecated
def auc_optimal(df: pd.DataFrame, validation: bool = True, computeTraces: bool = True) -> float:
    """
    Calculate the Optimal Area Under the Curve (AUC) for the given DataFrame.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing 'timeStamp' and 'y' columns.
    validation (bool): Whether to validate the DataFrame structure, by default True.
    computeTraces (bool): Whether to compute traces by sessionId, by default True.
    
    Returns:
    float: The computed optimal AUC value.
    """
    
    if(validation):
        validate_dataframe(df)

    if computeTraces:
        df = extract_traces_by_session(df)


    df = compute_space_time_diff(df)

    # Área bajo la línea óptima
    x0, y0 = df[ColumnNames.X].iloc[0], df[ColumnNames.Y].iloc[0]
    x1, y1 = df[ColumnNames.X].iloc[-1], df[ColumnNames.Y].iloc[-1]
    x_opt = np.linspace(x0, x1, len(df))
    y_opt = np.linspace(y0, y1, len(df))
    area_optimal = np.trapezoid(y_opt, x_opt)

    return area_optimal


@deprecated
def auc_ratio(df: pd.DataFrame, traces: dict[str, list[pd.DataFrame]] = None, per_traces: bool = True) -> dict:
    """
    Calculate the AUC ratio for the given DataFrame.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing 'timeStamp' and 'y' columns.
        computeTraces (bool): Whether to compute traces by sessionId, by default True. If False, df is assumed to be already segmented by sessionId.
    
    Returns:
        auc_per_session (dict): A dictionary with sessionId as keys and a tuple (auc, auc_ratio) as values. Where the auc is the area under the curve and auc_ratio is the ratio between the AUC and the optimal AUC.
    """

    if df is None and traces is None:
        raise ValueError("Either 'df' or 'traces' must be provided.")

    # if not per_traces:
        # Compute directly on the DataFrame (no trace extraction)
        # return auc_ratio_df(df)

    # If traces are not provided, extract them from df
    if traces is None:
        validate_dataframe(df)
        traces = extract_traces_by_session(df)

    return auc_ratio_traces(traces)


@deprecated
def auc_ratio_metrics(df: pd.DataFrame = None, computed_auc: dict = None, traces: dict[str, list[pd.DataFrame]] = None) -> dict:
    """
    This function computes the mean, max, and min auc ratio for each session on the given dataframe or list of traces.
    The optimal auc is not given in the output, only the auc ratio and auc, since it can be derived from them if needed.

    Parameters:
        df (pd.DataFrame): DataFrame containing interaction data.
        computed_auc (dict): Precomputed AUC ratios. If None, they will be computed from df or traces.
        traces (dict): A dictionary with keys as (sessionId) and values as lists of DataFrames. If None, traces will be computed from df.
    Returns:
        dict: A dictionary with keys as (sessionId) and values as dictionaries with 'mean_ratio', 'max_ratio', 'min_ratio' for the auc ratio and 'mean', 'max', and 'min' auc.
    """
    if (computed_auc is None):
        if(df is None):
            raise ValueError("Either 'df' or 'traces' must be provided.")
        if (traces is not None):
            computed_auc = auc_ratio(None, traces=traces, per_traces=True)
        else:
            computed_auc = auc_ratio(df)

    for session_id in computed_auc.keys():
        auc_ratios = [trace_metrics['auc_ratio'] for trace_metrics in computed_auc[session_id]]
        auc = [trace_metrics['auc'] for trace_metrics in computed_auc[session_id]]
        computed_auc[session_id] = {
            'mean_ratio': np.mean(auc_ratios) if auc_ratios else 0,
            'max_ratio': np.max(auc_ratios) if auc_ratios else 0,
            'min_ratio': np.min(auc_ratios) if auc_ratios else 0,
            'mean': np.mean(auc) if auc else 0,
            'max': np.max(auc) if auc else 0,
            'min': np.min(auc) if auc else 0,
        }
    return computed_auc
    

def deviations(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None) -> dict:
    """
    Calculate the Mean Absolute Deviation (MAD) for the given DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'y' column.
        traces (dict): A dictionary with keys as (sessionId) and values as lists of DataFrames. If None, traces will be computed from df.
    Returns:
        dict: A dictionary with keys as (sessionId) and values as dictionaries with 'mad_mean' (mean of maximum absolute deviations), 'mad_max' (maximum absolute deviation across all traces), 'mad_min' (minimum absolute deviation across all traces) and 'aad' (average absolute deviation).
    """
    
    validate_any_not_none(df, traces)

    if traces is None:
        validate_dataframe(df)
        traces = extract_traces_by_session(df)

    metrics = {}
    for session_id, session_traces in traces.items():
        session_average_absolute_deviation = []
        session_mad_max = []
        for trace in session_traces:
            session_average_absolute_deviation.append(np.mean(np.abs(trace[ColumnNames.Y] - trace[ColumnNames.Y].mean())))
            session_mad_max.append(np.max(np.abs(trace[ColumnNames.Y] - trace[ColumnNames.Y].mean())))
        metrics[session_id] = {
            ColumnNames.AAD: np.mean(session_average_absolute_deviation) if session_average_absolute_deviation else 0,
            ColumnNames.MAD_MAX: np.max(session_mad_max) if session_mad_max else 0,
            ColumnNames.MEAN_MAD: np.mean(session_mad_max) if session_mad_max else 0,
            ColumnNames.MIN_MAD: np.min(session_mad_max) if session_mad_max else 0,
        }

    return metrics

def angle(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None, per_traces: bool = True) -> pd.DataFrame | dict:
    """
    Angle formed by 3 consecutive points.
    Computed using formula:
    0i = arcos((yi+1-yi,xi+1-xi)*(yi-1-yi,xi-1-xi)/(di+1*di))

    Parameters:
        df (pd.DataFrame): DataFrame containing required columns.
        traces (dict): A dictionary with keys as (sessionId) and values as lists of DataFrames. If None, traces will be computed from df.
        per_traces (bool): Whether to compute the angle for each trace in the DataFrame. If False, the angle will be computed directly on the DataFrame.
    Returns:
        dict: A dictionary with keys as (sessionId) and values as lists of DataFrames with the 'angle' column.
    """
    validate_any_not_none(df, traces)

    if not per_traces:
        validate_dataframe(df)
        return _compute_angles(df)

    if traces is None:
        validate_dataframe(df)
        traces = extract_traces_by_session(df)

    for _, session_traces in traces.items():
        for trace in session_traces:
            _compute_angles(trace)
    return traces

def angular_velocity(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None, per_traces: bool = True) -> pd.DataFrame | dict:
    """
    Angular velocity computed as the change in angle over time.
    """
    validate_any_not_none(df, traces)
    
    if(df is not None):
        validate_dataframe(df)
        if not per_traces:
            if ColumnNames.ANGLE not in df.columns:
                df = angle(df, per_traces=False)
            if ColumnNames.DT not in df.columns:
                df = df.copy()
                timestamps = pd.to_numeric(df[ColumnNames.TIME_STAMP], errors="coerce")
                df[ColumnNames.DT] = timestamps.diff().fillna(0)
            return angular_velocity_df(df)
        if(ColumnNames.ANGLE not in df.columns):
            df = angle(df, traces)
            return _apply_metric_to_traces(df, angular_velocity_df)
        else:
            return angular_velocity_df(df)
 
    # If traces are not provided, extract them from df
    if traces is not None:
        return _apply_metric_to_traces(traces, angular_velocity_df)
    return traces

def angular_acceleration(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None, per_traces: bool = True) -> pd.DataFrame | dict:
    """
    Angular acceleration computed as the change in angular velocity over time.
    """
    # TODO per traces
    validate_any_not_none(df, traces)
    
    if(df is not None):
        validate_dataframe(df)
        if not per_traces:
            if ColumnNames.ANGULAR_VELOCITY not in df.columns:
                df = angular_velocity(df, per_traces=False)
            return angular_acceleration_df(df)
        if(ColumnNames.ANGULAR_VELOCITY not in df.columns):
            df = angular_velocity(df, per_traces=per_traces)
        if isinstance(df, dict):
            return _apply_metric_to_traces(df, angular_acceleration_df)
        return angular_acceleration_df(df)
 
        # If traces are not provided, extract them from df
    if traces is not None:
        return _apply_metric_to_traces(traces, angular_acceleration_df)
    return traces


def direction_changes(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None, per_traces: bool = False) -> pd.DataFrame | dict:
    """
        Calculate the number of direction changes in the given DataFrame.
        Parameters:
            df (pd.DataFrame): DataFrame containing 'x' and 'y' columns.
            traces (dict): A dictionary with keys as (sessionId) and values as lists of DataFrames. If None, traces will be computed from df.
            per_traces (bool): Whether to return the result for each trace separately. If False, returns the total count as an integer.
    """

    validate_any_not_none(df, traces)

    if not per_traces and df is not None:
        df = compute_space_time_diff(df)
        # Compute directly on the DataFrame (no trace extraction
        directions = np.arctan2(df[ColumnNames.DY], df[ColumnNames.DX])

        angle_diff = np.diff(directions)
        angle_diff = np.arctan2(np.sin(angle_diff), np.cos(angle_diff))

        # Calculate the changes in direction
        direction_changes = np.sum(np.abs(angle_diff) > np.pi / 4)  # Consider a change if the angle changes more than 45 degrees
        return direction_changes

    if traces is None and per_traces:
        validate_dataframe(df)
        traces = extract_traces_by_session(df)

    direction_changes_per_trace = {}
    for session_id, session_traces in traces.items():
        for trace in session_traces:
            trace = compute_space_time_diff(trace)
            directions = np.arctan2(trace[ColumnNames.DY], trace[ColumnNames.DX])
            angle_diff = np.diff(directions)
            angle_diff = np.arctan2(np.sin(angle_diff), np.cos(angle_diff))
            direction_changes = np.sum(np.abs(angle_diff) > np.pi / 4)  # Consider a change if the angle changes more than 45 degrees
            direction_changes_per_trace[session_id] = direction_changes
    
    return direction_changes_per_trace

def x_flips(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None, threshold: float = 0.1, per_traces: bool = False) -> int | dict:
    """
    Calculate the number of x-direction flips in the given DataFrame.
    
    **Metric Context Specificity**: If performed by trace, it will sum the flips of all traces in a session. 
    A session that has a flip between the end of a trace and the beginning of the next one will **not** be counted as a flip as computations are done trace by trace, so if you want to consider those flips, you should compute them on the whole dataframe or consider the traces as a single one.
    Parameters:
        df (pd.DataFrame): DataFrame containing 'x' and 'y' columns.
        traces (dict): A dictionary with keys as (sessionId) and values as lists of DataFrames. If None, traces will be computed from df.
        threshold (float): The threshold for considering a flip.
        per_traces (bool): Whether to return the result for each trace separately. If False, returns the total count as an integer.
    Returns:
    int | dict: The number of x-direction flips or a dictionary with the count for each session.
    """
    validate_any_not_none(df, traces)

    if not per_traces:
        validate_dataframe(df)
        if (ColumnNames.DX not in df.columns):
            df = compute_space_time_diff(df)
        return flips(df, column=ColumnNames.DX, threshold=threshold)
    
    if traces is None:
            validate_dataframe(df)
            traces = extract_traces_by_session(df)

    flips_per_session = {}
    if traces is not None:
        for session_id, session_traces in traces.items():
            for trace in session_traces:
                if (ColumnNames.DX not in trace.columns):
                    trace = compute_space_time_diff(trace)
                flips_per_session[session_id] = flips_per_session.get(session_id, 0) + flips(trace, column=ColumnNames.DX, threshold=threshold)

    return flips_per_session

def y_flips(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None, threshold: float = 0.1, per_traces: bool = False) -> int | dict:
    """
    Calculate the number of y-direction flips in the given DataFrame.

    **Metric Context Specificity**: If performed by trace, it will sum the flips of all traces in a session. 
    A session that has a flip between the end of a trace and the beginning of the next one will **not** be counted as a flip as computations are done trace by trace, so if you want to consider those flips, you should compute them on the whole dataframe or consider the traces as a single one.
    Parameters:
        df (pd.DataFrame): DataFrame containing 'x' and 'y' columns.
        traces (dict): A dictionary with keys as (sessionId) and values as lists of DataFrames. If None, traces will be computed from df.
        threshold (float): The threshold for considering a flip.
        per_traces (bool): Whether to return the result for each trace separately. If False, returns the total count as an integer.
    Returns:
        int | dict: The number of y-direction flips or a dictionary with the count for each session.
    """
    validate_any_not_none(df, traces)

    if not per_traces:
        validate_dataframe(df)
        if (ColumnNames.DY not in df.columns):
            df = compute_space_time_diff(df)
        return flips(df, column=ColumnNames.DY, threshold=threshold)
    
    if traces is None:
        validate_dataframe(df)
        traces = extract_traces_by_session(df)

    flips_per_session = {}
    if traces is not None:
        flips_per_session = {}
        for session_id, session_traces in traces.items():
            for trace in session_traces:
                if (ColumnNames.DY not in trace.columns):
                    trace = compute_space_time_diff(trace)
                flips_per_session[session_id] = flips_per_session.get(session_id, 0) + flips(trace, column=ColumnNames.DY, threshold=threshold)
    
    return flips_per_session

def curvature(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None) -> dict:
    """
    Calculate the curvature of the trajectory in the given DataFrame.
    Curvature is calculated as the change in direction over the change in distance.
    Parameters:
        df (pd.DataFrame): DataFrame containing 'x' and 'y' columns.
        traces (dict): A dictionary with keys as (sessionId) and values as lists of DataFrames. If None, traces will be computed from df.
    Returns:
        dict: A dictionary with keys as (sessionId) and values as the average curvature for that session.
    """
    
    validate_any_not_none(df, traces)

    if traces is None:
        validate_dataframe(df)
        traces = extract_traces_by_session(df)

    curvature_per_session = {}
    for session_id, session_traces in traces.items():
        curvatures = []
        for trace in session_traces:
            trace = compute_space_time_diff(trace)
            directions = np.arctan2(trace[ColumnNames.DY], trace[ColumnNames.DX])
            distance = trace[ColumnNames.DISTANCE]
            curvature = np.abs(np.diff(directions)) / distance[1:].values  # Curvature is change in direction over change in distance
            curvatures.append(np.mean(curvature))
        curvature_per_session[session_id] = np.mean(curvatures) if curvatures else 0
    
    return curvature_per_session

def inflections(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None) -> dict:
    """
    Calculate the number of inflection points in the trajectory of the given DataFrame.
    Inflection points are points where the curvature changes sign.
    Parameters:
        df (pd.DataFrame): DataFrame containing 'x' and 'y' columns.
        traces (dict): A dictionary with keys as (sessionId) and values as lists of DataFrames. If None, traces will be computed from df.
    Returns:
        dict: A dictionary with keys as (sessionId) and values as the number of inflection points for that session.
    """
    
    validate_any_not_none(df, traces)

    if traces is None:
        validate_dataframe(df)
        traces = extract_traces_by_session(df)

    inflections_per_session = {}
    for session_id, session_traces in traces.items():
        inflections = []
        for trace in session_traces:
            trace = compute_space_time_diff(trace)
            directions = np.arctan2(trace[ColumnNames.DY], trace[ColumnNames.DX])
            distance = trace[ColumnNames.DISTANCE]
            curvature = np.diff(directions) / distance[1:].values  # Curvature is change in direction over change in distance
            inflection_points = np.sum(np.diff(np.sign(curvature)) != 0)  # Count inflection points where curvature changes sign
            inflections.append(inflection_points)
        inflections_per_session[session_id] = np.sum(inflections)
    
    return inflections_per_session


def straigthness(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None) -> dict:
    """
    Calculate the straightness of the trajectory in the given DataFrame.
    Straightness is calculated as the ratio of the distance between the start and end points (ideal) to the total path length.
    Parameters:
        df (pd.DataFrame): DataFrame containing 'x' and 'y' columns.
        traces (dict): A dictionary with keys as (sessionId) and values as lists of DataFrames. If None, traces will be computed from df.
    Returns:
        dict: A dictionary with keys as (sessionId) and values as the straightness for that session.
    """
    
    validate_any_not_none(df, traces)

    if traces is None:
        validate_dataframe(df)
        traces = extract_traces_by_session(df)

    straightness_per_session = {}
    for session_id, session_traces in traces.items():
        straightness_values = []
        for trace in session_traces:
            trace = compute_space_time_diff(trace)
            trace = path(trace).get(session_id)[0] # TODO fix?
            start_point = np.array([trace[ColumnNames.X].iloc[0], trace[ColumnNames.Y].iloc[0]])
            end_point = np.array([trace[ColumnNames.X].iloc[-1], trace[ColumnNames.Y].iloc[-1]])
            ideal_distance = np.linalg.norm(end_point - start_point)
            path_length = trace[ColumnNames.DISTANCE].sum()
            straightness = ideal_distance / path_length if path_length > 0 else 0
            straightness_values.append(straightness)
        straightness_per_session[session_id] = np.mean(straightness_values) if straightness_values else 0

    return straightness_per_session

def jitter(df: pd.DataFrame = None, traces: dict[str, list[pd.DataFrame]] = None) -> dict:
    """
    Calculate the jitter of the trajectory in the given DataFrame.
    Jitter is calculated as the smoothed to real path length ratio.
    Parameters:
        df (pd.DataFrame): DataFrame containing 'x' and 'y' columns.
        traces (dict): A dictionary with keys as (sessionId) and values as lists of DataFrames. If None, traces will be computed from df.
    Returns:
        dict: A dictionary with keys as (sessionId) and values as the jitter for that session.
    """
    
    validate_any_not_none(df, traces)

    if traces is None:
        validate_dataframe(df)
        traces = extract_traces_by_session(df)

    raise NotImplementedError("Jitter is not implemented yet.")

