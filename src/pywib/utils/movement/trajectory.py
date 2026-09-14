
import numpy as np
from numpy.ma import angle
import pandas as pd

from pywib.constants import ColumnNames
from pywib.utils.utils import compute_space_time_diff, deprecated
from pywib.utils.validation import validate_dataframe


def _compute_angles(df: pd.DataFrame) -> pd.DataFrame:
    x_coordinates = pd.to_numeric(df[ColumnNames.X], errors="coerce").to_numpy(dtype=float)
    y_coordinates = pd.to_numeric(df[ColumnNames.Y], errors="coerce").to_numpy(dtype=float)
    df[ColumnNames.ANGLE] = np.nan
    angle_column = df.columns.get_loc(ColumnNames.ANGLE)

    for i in range(1, len(df) - 1):
        first_vector = np.array([
            y_coordinates[i] - y_coordinates[i - 1],
            x_coordinates[i] - x_coordinates[i - 1],
        ])
        second_vector = np.array([
            y_coordinates[i + 1] - y_coordinates[i],
            x_coordinates[i + 1] - x_coordinates[i],
        ])
        first_norm = np.linalg.norm(first_vector)
        second_norm = np.linalg.norm(second_vector)
        if not np.isfinite(first_norm) or not np.isfinite(second_norm) or first_norm == 0 or second_norm == 0:
            continue
        df.iloc[i, angle_column] = np.arccos(
            np.clip(np.dot(first_vector, second_vector) / (first_norm * second_norm), -1.0, 1.0)
        )

    return df


def _apply_metric_to_traces(traces: dict, metric) -> dict:
    for session_id, session_traces in traces.items():
        for index, trace in enumerate(session_traces):
            session_traces[index] = metric(trace)
        traces[session_id] = session_traces
    return traces

def angular_acceleration_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the angular acceleration for a given DataFrame.
    Angular acceleration is calculated as the change in angular velocity over time.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing 'timeStamp' and 'angular_velocity' columns.
    
    Returns:
        pd.DataFrame: DataFrame with an additional 'angular_acceleration' column representing the angular acceleration.
    """
    validate_dataframe(df)
    
    if ColumnNames.ANGULAR_VELOCITY not in df.columns:
        df = angular_velocity_df(df)

    if ColumnNames.DT not in df.columns:
        df = compute_space_time_diff(df)

    df[ColumnNames.ANGULAR_ACCELERATION] = np.where(
        df[ColumnNames.DT] != 0,
        df[ColumnNames.ANGULAR_VELOCITY].diff().fillna(0) / df[ColumnNames.DT],
        0,
    )
    return df

def angular_velocity_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the angular velocity for a given DataFrame.
    Angular velocity is calculated as the change in angle over time.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing 'timeStamp' and 'angle' columns.
    
    Returns:
        pd.DataFrame: DataFrame with an additional 'angular_velocity' column representing the angular velocity.
    """
    validate_dataframe(df)
    
    if(ColumnNames.DT not in df.columns):
        df = compute_space_time_diff(df)

    if ColumnNames.ANGLE not in df.columns:
        df = angle(df)

    df[ColumnNames.ANGLE] = df[ColumnNames.ANGLE].fillna(0)
    df[ColumnNames.ANGULAR_VELOCITY] = np.where(df[ColumnNames.DT] != 0, df[ColumnNames.ANGLE] / df[ColumnNames.DT], 0)
    return df

@deprecated
def _auc(df: pd.DataFrame) -> float:
    """
    Helper function to calculate the Area Under the Curve (AUC) for a single DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'x' and 'y' columns.
    Returns:
        float: The computed AUC value.
    """
    validate_dataframe(df)

    df = compute_space_time_diff(df)

    # Área bajo la curva real
    area_real = np.trapezoid(df[ColumnNames.Y], df[ColumnNames.X])
    return area_real

@deprecated
def _auc_optimal(df: pd.DataFrame) -> float:
    """
    Helper function to calculate the Area Under the Optimal Curve for a single DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'x' and 'y' columns.
    Returns:
        float: The computed Area Under the Optimal Curve value.
    """
    df = compute_space_time_diff(df)

    # Área bajo la línea óptima
    x0, y0 = df[ColumnNames.X].iloc[0], df[ColumnNames.Y].iloc[0]
    x1, y1 = df[ColumnNames.X].iloc[-1], df[ColumnNames.Y].iloc[-1]
    x_opt = np.linspace(x0, x1, len(df))
    y_opt = np.linspace(y0, y1, len(df))
    area_optimal = np.trapezoid(y_opt, x_opt)

    return area_optimal

def auc_df(df: pd.DataFrame) -> dict:
    """
    Calculate AUC and AUC ratio for a single DataFrame, returning them as a dictionary.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing 'x' and 'y' columns.
    Returns:
        tuple: A tuple (Geometric Auc, Execution Auc) as values.
    """
    validate_dataframe(df)
    

    return (_auc_geometric_deviation(df), _auc_execution_deviation(df)
    )

def auc_traces(traces: dict[str, list[pd.DataFrame]]) -> dict[str, list[tuple]]:
    """
    Calculate AUC and AUC ratio for a single DataFrame, returning them as a dictionary.
    
    Parameters:
        traces (pd.dict[str,list[pd.DataFrame]]): The traces with tthe sessionId as the key and the traces as values.
    Returns:
        dict: Dictionary sessionId as keys and a list with a tuple (Geometric Auc, Execution Auc) as values.
    """

    auc_sessions = {}
    for session_id, session_traces in traces.items():
        auc_per_trace = []
        for i, df in enumerate(session_traces):
            validate_dataframe(df)
            auc_per_trace.append(auc_df(df))
        auc_sessions[session_id] = auc_per_trace
    return auc_sessions

def _auc_geometric_deviation(df):
    df_opt = compute_optimal_path(df)
    # Prepare arrays
    user_x, user_y = df[ColumnNames.X].values, df[ColumnNames.Y].values
    opt_x, opt_y = df_opt[ColumnNames.X].values, df_opt[ColumnNames.Y].values

    # Compute perpendicular distances from optimal points to user segments
    dists = []
    for i in range(len(opt_x)):
        px, py = opt_x[i], opt_y[i]
        # Compute distance to all user segments and take minimum
        seg_dists = [
            point_to_segment_distance(px, py, user_x[j], user_y[j], user_x[j+1], user_y[j+1])
            for j in range(len(user_x)-1)
        ]
        dists.append(min(seg_dists))

    # Integrate along optimal path
    # Compute optimal path length increments (arc-length)
    dx = np.diff(opt_x)
    dy = np.diff(opt_y)
    ds = np.hypot(dx, dy)
    s_grid = np.concatenate(([0], np.cumsum(ds)))

    auc_perp = np.trapezoid(dists, s_grid)
    
    # Normalization by total optimal path length
    total_opt_length = s_grid[-1]
    if total_opt_length > 0:
        auc_perp /= total_opt_length
    return auc_perp

def _auc_execution_deviation(df):

    x = df[ColumnNames.X].to_numpy()
    y = df[ColumnNames.Y].to_numpy()

    if len(x) < 2:
        return 0.0

    # start and end
    x0, y0 = x[0], y[0]
    x1, y1 = x[-1], y[-1]

    # line coefficients
    a = y1 - y0
    b = x0 - x1
    c = x1*y0 - x0*y1

    denom = np.sqrt(a*a + b*b)

    # perpendicular distance to optimal line
    d = np.abs(a*x + b*y + c) / denom

    # arc-length along trajectory
    dx = np.diff(x)
    dy = np.diff(y)
    ds = np.sqrt(dx*dx + dy*dy)

    s = np.concatenate(([0], np.cumsum(ds)))

    # integrate deviation
    auc = np.trapezoid(d, s)

    # normalize by straight-line distance
    straight_dist = np.sqrt((x1-x0)**2 + (y1-y0)**2)

    if straight_dist > 0:
        auc /= straight_dist

    return auc

def compute_optimal_path(df: pd.DataFrame, n_points: int = 100) -> pd.DataFrame:
    """
    Compute an "optimal" trajectory as a straight line between start and end points
    of the user path, sampled uniformly with n_points.

    Parameters:
        df (pd.DataFrame): User trajectory with 'x' and 'y' columns.
        n_points (int): Number of points in the optimal path.

    Returns:
        pd.DataFrame: DataFrame with columns 'x' and 'y' representing the optimal path.
    """
    start_x, start_y = df[ColumnNames.X].iloc[0], df[ColumnNames.Y].iloc[0]
    end_x, end_y = df[ColumnNames.X].iloc[-1], df[ColumnNames.Y].iloc[-1]

    x_opt = np.linspace(start_x, end_x, n_points)
    y_opt = np.linspace(start_y, end_y, n_points)

    df_opt = pd.DataFrame({ColumnNames.X: x_opt, ColumnNames.Y: y_opt})
    return df_opt

def point_to_segment_distance(px, py, x1, y1, x2, y2):
        """Compute the shortest distance from point (px,py) to segment [(x1,y1),(x2,y2)]"""
        # Vector from x1,y1 to px,py
        dx, dy = x2 - x1, y2 - y1
        if dx == dy == 0:
            # Segment is a point
            return np.hypot(px - x1, py - y1)
        # Project point onto segment, computing parameter t
        t = ((px - x1) * dx + (py - y1) * dy) / (dx*dx + dy*dy)
        t = np.clip(t, 0, 1)
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        return np.hypot(px - closest_x, py - closest_y)

@deprecated
def auc_ratio_traces(traces: dict[str, list[pd.DataFrame]]) -> dict[list[dict]]:
    """
    Calculate AUC ratio metrics for multiple traces grouped by session IDs.

    Parameters:
        traces (dict[str, list[pd.DataFrame]]): Mapping of sessionId to list of DataFrames.
    Returns:
        dict[list[dict]]: Mapping of sessionId to list of AUC ratio metrics dictionaries.
    """
    auc_metrics = {}
    for session_id, session_traces in traces.items():
        auc_metrics_per_trace = []
        for i, df in enumerate(session_traces):
            validate_dataframe(df)
            # auc_metrics_per_trace.append(auc_ratio_df(df))
        auc_metrics[session_id] = auc_metrics_per_trace
    return auc_metrics

def flips(df: pd.DataFrame = None, column: str = ColumnNames.DX, threshold: float = 0.1) -> int:
    d_col = df[column].to_numpy()

    d_col_filtered = d_col[np.abs(d_col) > threshold]

    n_flips = np.sum(np.diff(np.sign(d_col_filtered)) != 0)

    return n_flips